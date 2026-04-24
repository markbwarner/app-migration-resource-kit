from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List

from .models import FileReport, ScanReport


def render_console_report(
    report: ScanReport,
    show_hint_breakdown: bool = False,
    include_file_reports: bool = False,
) -> str:
    lines: List[str] = []
    lines.append(f"Root path: {report.root_path}")
    lines.append(f"Files scanned: {report.files_scanned}")
    lines.append(f"Files with PII indicators: {report.files_with_pii}")
    lines.append(f"Total PII matches: {report.total_pii_matches}")
    lines.append(f"Potential JDBC-driver candidates: {report.jdbc_candidate_total}")
    lines.append(f"Potential code-change candidates: {report.code_change_candidate_total}")
    lines.append("")

    summary = _build_executive_summary(report)
    lines.extend(_render_executive_summary(summary))

    if not include_file_reports:
        return "\n".join(lines).rstrip() + "\n"

    if report.tables_summary:
        lines.append("Likely JDBC tables and sensitive columns:")
        for table_name, details in report.tables_summary.items():
            column_list = ", ".join(details["columns"])
            lines.append(
                f"  - {table_name} | columns: {column_list} | files: {details['file_count']}"
            )
        lines.append("")

    if report.totals_by_category:
        lines.append("Totals by category:")
        for category, count in sorted(report.totals_by_category.items()):
            lines.append(f"  - {category}: {count}")
        lines.append("")

    for file_report in report.file_reports:
        lines.append(f"File: {file_report.path}")
        lines.append(
            f"  Layer: {file_report.classification.layer} "
            f"(confidence {file_report.classification.confidence})"
        )
        lines.append(
            f"  LOC: {file_report.lines_of_code}, REST calls: {file_report.rest_call_count}, "
            f"SQL markers: {file_report.sql_statement_count}, JDBC markers: {file_report.jdbc_candidate_count}"
        )
        lines.append(
            f"  Service-call hints: {file_report.service_call_hint_count}, "
            f"Back-end hints: {file_report.backend_hint_count}, "
            f"Data-access/integration hints: {file_report.integration_hint_count}"
        )
        if show_hint_breakdown:
            if file_report.service_call_hint_breakdown:
                lines.append(
                    "  Service-call hint breakdown: "
                    + _format_breakdown(file_report.service_call_hint_breakdown)
                )
            if file_report.backend_hint_breakdown:
                lines.append(
                    "  Back-end hint breakdown: "
                    + _format_breakdown(file_report.backend_hint_breakdown)
                )
            if file_report.integration_hint_breakdown:
                lines.append(
                    "  Data-access/integration hint breakdown: "
                    + _format_breakdown(file_report.integration_hint_breakdown)
                )
        lines.append(
            f"  Potential JDBC-driver candidates: {file_report.jdbc_candidate_count}, "
            f"potential code-change candidates: {file_report.code_change_candidate_count}"
        )
        if file_report.sensitive_tables:
            lines.append("  Likely JDBC tables and sensitive columns:")
            for table_name, columns in sorted(file_report.sensitive_tables.items()):
                lines.append(f"    - {table_name}: {', '.join(columns)}")
        if file_report.ownership:
            ownership = file_report.ownership
            lines.append(
                f"  Likely change owner: {ownership.likely_change_owner} "
                f"(confidence {ownership.ownership_confidence})"
            )
            lines.append(
                f"  Role in flow: {ownership.role_in_flow}, "
                f"frontend_reference_only={ownership.frontend_reference_only}, "
                f"jdbc_substitution_candidate={ownership.jdbc_substitution_candidate}, "
                f"endpoint_correlation_score={ownership.endpoint_correlation_score}"
            )
            if ownership.matched_endpoints:
                lines.append("  Matched endpoints:")
                for endpoint in ownership.matched_endpoints:
                    lines.append(f"    - {endpoint}")
            if ownership.matched_payload_fields:
                lines.append("  Matched payload fields:")
                for field in ownership.matched_payload_fields:
                    lines.append(f"    - {field}")
            if ownership.likely_system_of_record_path:
                lines.append("  Likely system-of-record path:")
                for item in ownership.likely_system_of_record_path:
                    lines.append(f"    - {item}")
            if ownership.related_files:
                lines.append("  Related files:")
                for item in ownership.related_files:
                    lines.append(f"    - {item}")
            if ownership.rationale:
                lines.append("  Ownership rationale:")
                for item in ownership.rationale:
                    lines.append(f"    - {item}")
        if file_report.complexity:
            lines.append(
                f"  Complexity: {file_report.complexity.rating} "
                f"(score {file_report.complexity.score})"
            )
        if file_report.summary_by_category:
            lines.append("  Summary by category:")
            for category, count in sorted(file_report.summary_by_category.items()):
                lines.append(f"    - {category}: {count}")
        if file_report.pii_matches:
            lines.append("  Matches:")
            for match in file_report.pii_matches:
                lines.append(
                    f"    - line {match.line_number}: {match.attribute} -> "
                    f"{match.category} [{match.detector}, {match.confidence}]"
                    + (f" pattern={match.pattern_name}" if match.pattern_name else "")
                )
        if file_report.notes:
            lines.append("  Notes:")
            for note in file_report.notes:
                lines.append(f"    - {note}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _render_executive_summary(summary: Dict) -> List[str]:
    lines: List[str] = []
    lines.append("Executive summary:")

    owner_counts = summary["likely_change_owner_summary"]
    if owner_counts:
        lines.append("  Likely change owner summary:")
        for owner, count in sorted(owner_counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"    - {owner}: {count}")

    action_counts = summary["recommended_change_action_summary"]
    if action_counts:
        lines.append("  Recommended change action summary:")
        for action, count in sorted(action_counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"    - {action}: {count}")

    role_counts = summary["role_in_flow_summary"]
    if role_counts:
        lines.append("  Role in flow summary:")
        for role, count in sorted(role_counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"    - {role}: {count}")

    complexity_counts = summary["complexity_distribution"]
    if complexity_counts:
        lines.append("  Complexity distribution:")
        for rating in ("low", "medium", "high"):
            if rating in complexity_counts:
                lines.append(f"    - {rating}: {complexity_counts[rating]}")

    frontend_correlations = summary["frontend_to_backend_correlations"]
    if frontend_correlations:
        lines.append("  Front-end to back-end correlations:")
        for item in frontend_correlations:
            lines.append(
                f"    - {item['source_file']} -> {', '.join(item['related_files'])} "
                f"(score {item['score']})"
            )

    backend_correlations = summary["backend_to_data_access_correlations"]
    if backend_correlations:
        lines.append("  Back-end to data-access correlations:")
        for item in backend_correlations:
            lines.append(
                f"    - {item['source_file']} -> {', '.join(item['related_files'])} "
                f"(score {item['score']})"
            )

    if summary["tables_summary"]:
        lines.append("  Likely JDBC tables and sensitive columns:")
        for table_name, details in list(summary["tables_summary"].items())[:8]:
            lines.append(
                f"    - {table_name}: {', '.join(details['columns'])} "
                f"(files {details['file_count']})"
            )

    lines.append("")
    return lines


def _format_breakdown(breakdown: Dict[str, int]) -> str:
    items = sorted(breakdown.items(), key=lambda item: (-item[1], item[0]))
    return ", ".join(f"{pattern}({count})" for pattern, count in items)


def write_json_report(
    report: ScanReport,
    output_path: Path,
    include_file_reports: bool = False,
) -> None:
    output_path.write_text(
        json.dumps(_serialize_report(report, include_file_reports=include_file_reports), indent=2),
        encoding="utf-8",
    )


def write_json_summary(report: ScanReport, output_path: Path) -> None:
    output_path.write_text(
        json.dumps(_serialize_summary_report(report), indent=2),
        encoding="utf-8",
    )


def write_json_file_reports(report: ScanReport, output_path: Path) -> None:
    output_path.write_text(
        json.dumps([_serialize_file_report(file_report) for file_report in report.file_reports], indent=2),
        encoding="utf-8",
    )


def write_change_targets_csv(report: ScanReport, output_path: Path) -> None:
    fieldnames = [
        "path",
        "likely_change_target",
        "recommended_change_action",
        "likely_change_owner",
        "ownership_confidence",
        "role_in_flow",
        "frontend_reference_only",
        "jdbc_substitution_candidate",
        "backend_owner_confidence",
        "endpoint_correlation_score",
        "code_change_candidate_count",
        "jdbc_candidate_count",
        "sql_verbs",
        "sql_data_action",
        "complexity_rating",
        "complexity_score",
        "matched_endpoints",
        "matched_payload_fields",
        "likely_system_of_record_path",
        "related_files",
        "jdbc_tables",
        "sensitive_columns",
        "sensitive_tables",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for file_report in report.file_reports:
            if not file_report.ownership or not file_report.ownership.likely_change_target:
                continue
            writer.writerow(
                {
                    "path": file_report.path,
                    "likely_change_target": file_report.ownership.likely_change_target,
                    "recommended_change_action": file_report.ownership.recommended_change_action,
                    "likely_change_owner": file_report.ownership.likely_change_owner,
                    "ownership_confidence": file_report.ownership.ownership_confidence,
                    "role_in_flow": file_report.ownership.role_in_flow,
                    "frontend_reference_only": file_report.ownership.frontend_reference_only,
                    "jdbc_substitution_candidate": file_report.ownership.jdbc_substitution_candidate,
                    "backend_owner_confidence": file_report.ownership.backend_owner_confidence,
                    "endpoint_correlation_score": file_report.ownership.endpoint_correlation_score,
                    "code_change_candidate_count": file_report.code_change_candidate_count,
                    "jdbc_candidate_count": file_report.jdbc_candidate_count,
                    "sql_verbs": " | ".join(file_report.sql_verbs),
                    "sql_data_action": file_report.sql_data_action,
                    "complexity_rating": file_report.complexity.rating if file_report.complexity else "",
                    "complexity_score": file_report.complexity.score if file_report.complexity else "",
                    "matched_endpoints": " | ".join(file_report.ownership.matched_endpoints),
                    "matched_payload_fields": " | ".join(file_report.ownership.matched_payload_fields),
                    "likely_system_of_record_path": " | ".join(file_report.ownership.likely_system_of_record_path),
                    "related_files": " | ".join(file_report.ownership.related_files),
                    "jdbc_tables": " | ".join(sorted(file_report.sensitive_tables)),
                    "sensitive_columns": " | ".join(_flatten_sensitive_columns(file_report.sensitive_tables)),
                    "sensitive_tables": " | ".join(
                        f"{table}:{','.join(columns)}"
                        for table, columns in sorted(file_report.sensitive_tables.items())
                    ),
                }
            )


def write_file_reports_csv(report: ScanReport, output_path: Path) -> None:
    fieldnames = [
        "path",
        "layer",
        "classification_confidence",
        "classification_reasons",
        "lines_of_code",
        "summary_by_category",
        "jdbc_candidate_count",
        "code_change_candidate_count",
        "rest_call_count",
        "sql_statement_count",
        "endpoint_count",
        "service_call_hint_count",
        "backend_hint_count",
        "integration_hint_count",
        "sql_verbs",
        "sql_data_action",
        "likely_change_target",
        "recommended_change_action",
        "likely_change_owner",
        "ownership_confidence",
        "role_in_flow",
        "frontend_reference_only",
        "backend_owner_confidence",
        "jdbc_substitution_candidate",
        "endpoint_correlation_score",
        "matched_endpoints",
        "matched_payload_fields",
        "likely_system_of_record_path",
        "related_files",
        "jdbc_tables",
        "sensitive_columns",
        "sensitive_tables",
        "complexity_rating",
        "complexity_score",
        "complexity_rationale",
        "notes",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for file_report in report.file_reports:
            ownership = file_report.ownership
            writer.writerow(
                {
                    "path": file_report.path,
                    "layer": file_report.classification.layer,
                    "classification_confidence": file_report.classification.confidence,
                    "classification_reasons": " | ".join(file_report.classification.reasons),
                    "lines_of_code": file_report.lines_of_code,
                    "summary_by_category": " | ".join(
                        f"{category}:{count}"
                        for category, count in sorted(file_report.summary_by_category.items())
                    ),
                    "jdbc_candidate_count": file_report.jdbc_candidate_count,
                    "code_change_candidate_count": file_report.code_change_candidate_count,
                    "rest_call_count": file_report.rest_call_count,
                    "sql_statement_count": file_report.sql_statement_count,
                    "endpoint_count": file_report.endpoint_count,
                    "service_call_hint_count": file_report.service_call_hint_count,
                    "backend_hint_count": file_report.backend_hint_count,
                    "integration_hint_count": file_report.integration_hint_count,
                    "sql_verbs": " | ".join(file_report.sql_verbs),
                    "sql_data_action": file_report.sql_data_action,
                    "likely_change_target": ownership.likely_change_target if ownership else "",
                    "recommended_change_action": ownership.recommended_change_action if ownership else "",
                    "likely_change_owner": ownership.likely_change_owner if ownership else "",
                    "ownership_confidence": ownership.ownership_confidence if ownership else "",
                    "role_in_flow": ownership.role_in_flow if ownership else "",
                    "frontend_reference_only": ownership.frontend_reference_only if ownership else "",
                    "backend_owner_confidence": ownership.backend_owner_confidence if ownership else "",
                    "jdbc_substitution_candidate": ownership.jdbc_substitution_candidate if ownership else "",
                    "endpoint_correlation_score": ownership.endpoint_correlation_score if ownership else "",
                    "matched_endpoints": " | ".join(ownership.matched_endpoints) if ownership else "",
                    "matched_payload_fields": " | ".join(ownership.matched_payload_fields) if ownership else "",
                    "likely_system_of_record_path": " | ".join(ownership.likely_system_of_record_path) if ownership else "",
                    "related_files": " | ".join(ownership.related_files) if ownership else "",
                    "jdbc_tables": " | ".join(sorted(file_report.sensitive_tables)),
                    "sensitive_columns": " | ".join(_flatten_sensitive_columns(file_report.sensitive_tables)),
                    "sensitive_tables": " | ".join(
                        f"{table}:{','.join(columns)}"
                        for table, columns in sorted(file_report.sensitive_tables.items())
                    ),
                    "complexity_rating": file_report.complexity.rating if file_report.complexity else "",
                    "complexity_score": file_report.complexity.score if file_report.complexity else "",
                    "complexity_rationale": " | ".join(file_report.complexity.rationale) if file_report.complexity else "",
                    "notes": " | ".join(file_report.notes),
                }
            )


def write_dba_planning_sql(report: ScanReport, output_path: Path) -> None:
    lines: List[str] = []
    lines.append("-- DBA planning SQL generated from jdbc_candidate files")
    lines.append("--")
    lines.append("-- Notes:")
    lines.append("-- 1. DESCRIBE is common in MySQL-family tools and some SQL consoles.")
    lines.append("--    Oracle SQL*Plus-style environments often use DESC, and some databases")
    lines.append("--    require INFORMATION_SCHEMA or catalog queries instead.")
    lines.append("-- 2. The max-length checks below use LENGTH(column), which is valid in")
    lines.append("--    Oracle, PostgreSQL, and MySQL. SQL Server typically uses LEN(column).")
    lines.append("")

    jdbc_tables = _collect_jdbc_candidate_tables(report)
    for table_name, details in jdbc_tables.items():
        columns = details["columns"]
        source_files = details["source_files"]
        lines.append(f"-- Table: {table_name}")
        lines.append(f"-- Source files: {', '.join(source_files)}")
        lines.append(f"describe {table_name};")
        lines.append("")
        if columns:
            lines.append(f"-- Max current lengths for sensitive columns in {table_name}")
            lines.append("select")
            select_lines = [
                f"  max(length({column})) as max_{column}_length"
                for column in columns
            ]
            lines.append(",\n".join(select_lines))
            lines.append(f"from {table_name};")
            lines.append("")

    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _serialize_report(report: ScanReport, include_file_reports: bool = False) -> Dict:
    summary = _build_executive_summary(report)
    payload = {
        "root_path": report.root_path,
        "files_scanned": report.files_scanned,
        "files_with_pii": report.files_with_pii,
        "total_pii_matches": report.total_pii_matches,
        "jdbc_candidate_total": report.jdbc_candidate_total,
        "code_change_candidate_total": report.code_change_candidate_total,
        "totals_by_category": report.totals_by_category,
        "executive_summary": summary,
        "tables_summary": report.tables_summary,
    }
    if include_file_reports:
        payload["file_reports"] = [_serialize_file_report(file_report) for file_report in report.file_reports]
    return payload


def _serialize_summary_report(report: ScanReport) -> Dict:
    return _serialize_report(report, include_file_reports=False)


def _flatten_sensitive_columns(sensitive_tables: Dict[str, List[str]]) -> List[str]:
    columns = {
        column
        for per_table_columns in sensitive_tables.values()
        for column in per_table_columns
    }
    return sorted(columns)


def _collect_jdbc_candidate_tables(report: ScanReport) -> Dict[str, Dict[str, List[str]]]:
    tables: Dict[str, Dict[str, List[str]]] = {}
    for file_report in report.file_reports:
        if not file_report.ownership:
            continue
        if file_report.ownership.recommended_change_action != "review_jdbc_substitution":
            continue
        for table_name, columns in sorted(file_report.sensitive_tables.items()):
            entry = tables.setdefault(
                table_name,
                {"columns": [], "source_files": []},
            )
            entry["columns"] = sorted(set(entry["columns"]) | set(columns))
            entry["source_files"] = sorted(
                set(entry["source_files"]) | {Path(file_report.path).name}
            )
    return tables


def _build_executive_summary(report: ScanReport) -> Dict:
    owner_counts = Counter(
        file_report.ownership.likely_change_owner
        for file_report in report.file_reports
        if file_report.ownership
    )
    role_counts = Counter(
        file_report.ownership.role_in_flow
        for file_report in report.file_reports
        if file_report.ownership
    )
    action_counts = Counter(
        file_report.ownership.recommended_change_action
        for file_report in report.file_reports
        if file_report.ownership
    )
    complexity_counts = Counter(
        file_report.complexity.rating
        for file_report in report.file_reports
        if file_report.complexity
    )
    return {
        "likely_change_owner_summary": dict(sorted(owner_counts.items())),
        "recommended_change_action_summary": dict(sorted(action_counts.items())),
        "role_in_flow_summary": dict(sorted(role_counts.items())),
        "complexity_distribution": dict(sorted(complexity_counts.items())),
        "frontend_to_backend_correlations": _summarize_correlations(
            report.file_reports,
            correlation_type="frontend",
        ),
        "backend_to_data_access_correlations": _summarize_correlations(
            report.file_reports,
            correlation_type="backend",
        ),
        "tables_summary": report.tables_summary,
    }


def _summarize_correlations(file_reports: List[FileReport], correlation_type: str) -> List[Dict]:
    if correlation_type == "frontend":
        candidates = [
            file_report
            for file_report in file_reports
            if file_report.ownership
            and file_report.ownership.frontend_reference_only
            and file_report.ownership.related_files
        ]
    else:
        candidates = [
            file_report
            for file_report in file_reports
            if file_report.ownership
            and file_report.ownership.likely_change_owner == "backend_logic_owner"
            and file_report.ownership.related_files
        ]

    candidates = sorted(
        candidates,
        key=lambda item: item.ownership.endpoint_correlation_score,
        reverse=True,
    )[:5]
    return [
        {
            "source_file": Path(file_report.path).name,
            "related_files": [Path(path).name for path in file_report.ownership.related_files[:2]],
            "score": file_report.ownership.endpoint_correlation_score,
        }
        for file_report in candidates
    ]


def _serialize_file_report(file_report: FileReport) -> Dict:
    return {
        "path": file_report.path,
        "lines_of_code": file_report.lines_of_code,
        "classification": {
            "layer": file_report.classification.layer,
            "confidence": file_report.classification.confidence,
            "reasons": file_report.classification.reasons,
        },
        "summary_by_category": file_report.summary_by_category,
        "jdbc_candidate_count": file_report.jdbc_candidate_count,
        "code_change_candidate_count": file_report.code_change_candidate_count,
        "rest_call_count": file_report.rest_call_count,
        "sql_statement_count": file_report.sql_statement_count,
        "sql_verbs": file_report.sql_verbs,
        "sql_data_action": file_report.sql_data_action,
        "endpoint_count": file_report.endpoint_count,
        "service_call_hint_count": file_report.service_call_hint_count,
        "backend_hint_count": file_report.backend_hint_count,
        "integration_hint_count": file_report.integration_hint_count,
        "service_call_hint_breakdown": file_report.service_call_hint_breakdown,
        "backend_hint_breakdown": file_report.backend_hint_breakdown,
        "integration_hint_breakdown": file_report.integration_hint_breakdown,
        "sensitive_tables": file_report.sensitive_tables,
        "ownership": {
            "likely_change_owner": file_report.ownership.likely_change_owner,
            "likely_change_target": file_report.ownership.likely_change_target,
            "recommended_change_action": file_report.ownership.recommended_change_action,
            "ownership_confidence": file_report.ownership.ownership_confidence,
            "role_in_flow": file_report.ownership.role_in_flow,
            "frontend_reference_only": file_report.ownership.frontend_reference_only,
            "backend_owner_confidence": file_report.ownership.backend_owner_confidence,
            "jdbc_substitution_candidate": file_report.ownership.jdbc_substitution_candidate,
            "endpoint_correlation_score": file_report.ownership.endpoint_correlation_score,
            "matched_endpoints": file_report.ownership.matched_endpoints,
            "matched_payload_fields": file_report.ownership.matched_payload_fields,
            "likely_system_of_record_path": file_report.ownership.likely_system_of_record_path,
            "related_files": file_report.ownership.related_files,
            "rationale": file_report.ownership.rationale,
        }
        if file_report.ownership
        else None,
        "complexity": {
            "score": file_report.complexity.score,
            "rating": file_report.complexity.rating,
            "rationale": file_report.complexity.rationale,
        }
        if file_report.complexity
        else None,
        "notes": file_report.notes,
        "pii_matches": [
            {
                "line_number": match.line_number,
                "attribute": match.attribute,
                "category": match.category,
                "detector": match.detector,
                "confidence": match.confidence,
                "impact_hint": match.impact_hint,
                "pattern_name": match.pattern_name,
            }
            for match in file_report.pii_matches
        ],
    }
