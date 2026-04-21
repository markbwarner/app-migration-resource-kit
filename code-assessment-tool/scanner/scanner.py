from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Callable, Iterable, List, Sequence

from .classifiers import analyze_hint_breakdowns, classify_file, count_integration_markers
from .config import DEFAULT_EXCLUDES, CustomKeywordRule, CustomRegexRule, is_source_file
from .detectors import build_presidio_analyzer, detect_custom_regex_matches, detect_keyword_matches, detect_presidio_matches
from .models import ComplexityAssessment, FileReport, PiiMatch, ScanReport
from .ownership import assess_ownership, correlate_ownership, extract_endpoints, extract_payload_fields, extract_sensitive_table_map, extract_system_of_record_paths


def scan_directory(
    root_path: Path,
    exclude_dirs: Sequence[str] | None = None,
    custom_rules: Sequence[CustomKeywordRule] | None = None,
    custom_regex_rules: Sequence[CustomRegexRule] | None = None,
    suppress_default_on_custom_match: bool = False,
    use_presidio: bool = False,
    progress_callback: Callable[[str], None] | None = None,
) -> ScanReport:
    excludes = set(DEFAULT_EXCLUDES)
    if exclude_dirs:
        excludes.update(exclude_dirs)

    analyzer = build_presidio_analyzer() if use_presidio else None
    file_reports: List[FileReport] = []
    all_reports: List[FileReport] = []
    totals_by_category: Counter[str] = Counter()
    tables_summary: dict[str, dict[str, set[str] | int]] = {}
    total_pii_matches = 0
    jdbc_candidate_total = 0
    code_change_candidate_total = 0
    files_scanned = 0

    source_files = sorted(_iter_source_files(root_path, excludes))
    total_files = len(source_files)
    if progress_callback:
        progress_callback(f"Discovered {total_files} source files to scan under {root_path}")

    for index, file_path in enumerate(source_files, start=1):
        files_scanned += 1
        if progress_callback:
            progress_callback(f"[{index}/{total_files}] Scanning {file_path}")
        report = _scan_file(
            file_path,
            analyzer,
            custom_rules or [],
            custom_regex_rules or [],
            suppress_default_on_custom_match,
        )
        all_reports.append(report)
        if not report.pii_matches:
            continue
        file_reports.append(report)
        total_pii_matches += len(report.pii_matches)
        jdbc_candidate_total += report.jdbc_candidate_count
        code_change_candidate_total += report.code_change_candidate_count
        totals_by_category.update(report.summary_by_category)
        _merge_tables_summary(tables_summary, report)

    correlate_ownership(all_reports)

    return ScanReport(
        root_path=str(root_path),
        files_scanned=files_scanned,
        files_with_pii=len(file_reports),
        total_pii_matches=total_pii_matches,
        file_reports=file_reports,
        totals_by_category=dict(totals_by_category),
        tables_summary=_finalize_tables_summary(tables_summary),
        jdbc_candidate_total=jdbc_candidate_total,
        code_change_candidate_total=code_change_candidate_total,
    )


def _iter_source_files(root_path: Path, excludes: set[str]) -> Iterable[Path]:
    for path in root_path.rglob("*"):
        if not path.is_file():
            continue
        if any(part in excludes for part in path.parts):
            continue
        if is_source_file(path):
            yield path


def _scan_file(
    file_path: Path,
    analyzer,
    custom_rules: Sequence[CustomKeywordRule],
    custom_regex_rules: Sequence[CustomRegexRule],
    suppress_default_on_custom_match: bool,
) -> FileReport:
    content = _safe_read(file_path)
    lines = content.splitlines()
    classification = classify_file(file_path, content)
    rest_calls, sql_count, endpoint_count, jdbc_markers = count_integration_markers(content)
    service_call_hint_breakdown, backend_hint_breakdown, integration_hint_breakdown = analyze_hint_breakdowns(content)
    endpoints = extract_endpoints(file_path, content)
    payload_fields = extract_payload_fields(content)

    pii_matches: List[PiiMatch] = []
    for index, line in enumerate(lines, start=1):
        pii_matches.extend(
            detect_keyword_matches(
                index,
                line,
                custom_rules,
                suppress_default_on_custom_match=suppress_default_on_custom_match,
            )
        )
        pii_matches.extend(detect_custom_regex_matches(index, line, custom_regex_rules))
        pii_matches.extend(detect_presidio_matches(index, line, analyzer))

    pii_matches = _dedupe_and_sort(pii_matches)
    category_counts = Counter(match.category for match in pii_matches)
    system_of_record_paths = extract_system_of_record_paths(content, pii_matches)
    sensitive_tables = extract_sensitive_table_map(content, pii_matches)
    jdbc_candidate_count, code_change_candidate_count, notes = _estimate_migration_paths(
        classification.layer,
        pii_matches,
        jdbc_markers,
        rest_calls,
        sql_count,
    )
    ownership = assess_ownership(
        file_path,
        content,
        classification.layer,
        endpoints,
        payload_fields,
        system_of_record_paths,
        pii_matches,
        rest_calls,
        sql_count,
        jdbc_markers,
        endpoint_count,
    )
    jdbc_candidate_count, code_change_candidate_count, notes = _apply_ownership_adjustments(
        ownership,
        jdbc_candidate_count,
        code_change_candidate_count,
        notes,
    )
    complexity = _assess_complexity(
        len(lines),
        len(pii_matches),
        jdbc_candidate_count,
        code_change_candidate_count,
        rest_calls,
        sql_count,
        classification.layer,
    )

    return FileReport(
        path=str(file_path),
        lines_of_code=len(lines),
        classification=classification,
        pii_matches=pii_matches,
        summary_by_category=dict(category_counts),
        jdbc_candidate_count=jdbc_candidate_count,
        code_change_candidate_count=code_change_candidate_count,
        rest_call_count=rest_calls,
        sql_statement_count=sql_count,
        endpoint_count=endpoint_count,
        service_call_hint_count=sum(service_call_hint_breakdown.values()),
        backend_hint_count=sum(backend_hint_breakdown.values()),
        integration_hint_count=sum(integration_hint_breakdown.values()),
        service_call_hint_breakdown=service_call_hint_breakdown,
        backend_hint_breakdown=backend_hint_breakdown,
        integration_hint_breakdown=integration_hint_breakdown,
        sensitive_tables=sensitive_tables,
        ownership=ownership,
        complexity=complexity,
        notes=notes,
    )


def _merge_tables_summary(
    tables_summary: dict[str, dict[str, set[str] | int]],
    report: FileReport,
) -> None:
    for table_name, columns in report.sensitive_tables.items():
        entry = tables_summary.setdefault(
            table_name,
            {"columns": set(), "files": set(), "match_count": 0},
        )
        entry["columns"].update(columns)
        entry["files"].add(report.path)
        entry["match_count"] += len(columns)


def _finalize_tables_summary(
    tables_summary: dict[str, dict[str, set[str] | int]],
) -> dict[str, dict[str, List[str] | int]]:
    finalized: dict[str, dict[str, List[str] | int]] = {}
    for table_name, data in tables_summary.items():
        finalized[table_name] = {
            "columns": sorted(data["columns"]),
            "files": sorted(data["files"]),
            "file_count": len(data["files"]),
            "match_count": int(data["match_count"]),
        }
    return dict(sorted(finalized.items()))


def _apply_ownership_adjustments(
    ownership,
    jdbc_candidate_count: int,
    code_change_candidate_count: int,
    notes: Sequence[str],
) -> tuple[int, int, List[str]]:
    adjusted_notes = list(notes)
    if ownership.likely_change_owner == "supporting_model":
        return (
            0,
            0,
            [
                "Supporting model/DTO file. Sensitive-field references here usually describe payload shape rather than the primary CRDP implementation point."
            ],
        )
    return jdbc_candidate_count, code_change_candidate_count, adjusted_notes


def _estimate_migration_paths(
    layer: str,
    pii_matches: Sequence[PiiMatch],
    jdbc_markers: int,
    rest_calls: int,
    sql_count: int,
) -> tuple[int, int, List[str]]:
    notes: List[str] = []
    pii_count = len(pii_matches)
    jdbc_candidate_count = 0
    code_change_candidate_count = 0

    if layer == "frontend_with_service_calls" or layer == "frontend":
        code_change_candidate_count = 0
        jdbc_candidate_count = 0
        notes.append("Likely front-end code. PII references may only drive UI or payload shape; CRDP changes are more likely needed in back-end/data layers.")
        return jdbc_candidate_count, code_change_candidate_count, notes

    if layer in {"data_access", "backend_with_data_access"}:
        jdbc_candidate_count = min(pii_count, max(1, jdbc_markers + sql_count))
        residual = max(0, pii_count - jdbc_candidate_count)
        code_change_candidate_count = residual
        notes.append("Data-access markers found. Thales JDBC driver may cover part of the migration with lower application-code impact.")
        if residual:
            notes.append("Some PII references are outside direct JDBC/SQL indicators and may still need targeted code review.")
        return jdbc_candidate_count, code_change_candidate_count, notes

    if layer == "backend":
        if rest_calls > 0:
            code_change_candidate_count = pii_count
            notes.append("Back-end service appears to orchestrate calls or transformations. CRDP REST integration may require code changes here.")
        else:
            code_change_candidate_count = max(1, pii_count // 2)
            notes.append("Back-end logic contains PII references but limited data-access indicators. Manual review needed to confirm CRDP touchpoints.")
        return jdbc_candidate_count, code_change_candidate_count, notes

    code_change_candidate_count = pii_count
    notes.append("Unknown layer. Treat as code-review candidate until architecture is confirmed.")
    return jdbc_candidate_count, code_change_candidate_count, notes


def _assess_complexity(
    loc: int,
    pii_count: int,
    jdbc_candidate_count: int,
    code_change_candidate_count: int,
    rest_calls: int,
    sql_count: int,
    layer: str,
) -> ComplexityAssessment:
    score = 0.0
    rationale: List[str] = []

    score += min(25.0, loc / 40.0)
    score += pii_count * 2.5
    score += code_change_candidate_count * 3.0
    score += rest_calls * 1.5
    score += sql_count * 1.0
    score -= jdbc_candidate_count * 1.5

    if layer.startswith("frontend"):
        score -= 6
        rationale.append("Front-end only files usually have lower direct CRDP migration impact.")
    if jdbc_candidate_count:
        rationale.append("JDBC-driver coverage lowers implementation complexity, but validation/testing is still required.")
    if code_change_candidate_count:
        rationale.append("Potential service-layer code changes increase complexity and testing scope.")
    if loc > 300:
        rationale.append("Large files increase review and regression-test effort.")

    score = max(1.0, round(score, 1))
    if score < 12:
        rating = "low"
    elif score < 24:
        rating = "medium"
    else:
        rating = "high"
    return ComplexityAssessment(score=score, rating=rating, rationale=rationale)


def _dedupe_and_sort(matches: Iterable[PiiMatch]) -> List[PiiMatch]:
    seen = set()
    ordered: List[PiiMatch] = []
    for match in sorted(matches, key=lambda item: (item.line_number, item.attribute.lower(), item.category)):
        key = (match.line_number, match.attribute.lower(), match.category)
        if key not in seen:
            seen.add(key)
            ordered.append(match)
    return ordered


def _safe_read(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="latin-1", errors="ignore")
