from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Sequence
from urllib.parse import urlparse

from .models import FileReport, OwnershipAssessment, PiiMatch


SPRING_REQUEST_MAPPING_VALUE_RE = re.compile(r'@RequestMapping\s*\(\s*"([^"]+)"')
SPRING_METHOD_MAPPING_RE = re.compile(
    r'@(?:Get|Post|Put|Delete|Patch|Request)Mapping\s*\(\s*"([^"]+)"'
)
DOTNET_ROUTE_RE = re.compile(r'\[Route\("([^"]+)"\)\]')
DOTNET_HTTP_METHOD_RE = re.compile(r'\[Http(?:Get|Post|Put|Delete|Patch)(?:\("([^"]*)"\))?\]')
FETCH_URL_RE = re.compile(r'fetch\(\s*["\']([^"\']+)["\']', re.IGNORECASE)
AXIOS_URL_RE = re.compile(
    r'axios\.(?:get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']',
    re.IGNORECASE,
)
APP_ROUTE_RE = re.compile(r'app\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']', re.IGNORECASE)
ROUTER_ROUTE_RE = re.compile(r'router\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']', re.IGNORECASE)
KEY_VALUE_RE = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*:')
JSON_KEY_RE = re.compile(r'"([A-Za-z_][A-Za-z0-9_]*)"\s*:')
JAVA_RECORD_FIELD_RE = re.compile(r'\b(?:record|class)\s+\w+\s*\((.*?)\)', re.DOTALL)
JAVA_RECORD_ARG_RE = re.compile(
    r'(?:[A-Z][A-Za-z0-9_<>?]*|String|Integer|Long|Double|Boolean|BigDecimal|LocalDate|LocalDateTime|Date|UUID)\s+([A-Za-z_][A-Za-z0-9_]*)'
)
JAVA_METHOD_CALL_FIELD_RE = re.compile(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\(')
CSHARP_PROPERTY_RE = re.compile(
    r'\b(?:public|private|protected|internal)\s+[A-Za-z0-9_<>,.?]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{'
)
TS_FIELD_RE = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*[^=;]+[;,]?\s*$', re.MULTILINE)
SQL_COLUMN_RE = re.compile(r'\b([a-z][a-z0-9_]{2,})\b')
SQL_TABLE_RE = re.compile(r'\b(?:from|join|update|insert\s+into)\s+([a-zA-Z_][a-zA-Z0-9_.$]*)', re.IGNORECASE)
CLASS_RE = re.compile(r'\b(?:public\s+)?(?:final\s+)?class\s+\w+')
METHOD_RE = re.compile(
    r'\b(?:public|private|protected|internal)\s+[A-Za-z0-9_<>,.?[\]]+\s+\w+\s*\([^)]*\)\s*\{'
)
SUPPORTING_FILE_TOKENS = (
    "request",
    "response",
    "dto",
    "model",
    "payload",
    "entity",
    "profile",
    "result",
    "record",
)
ORCHESTRATION_TOKENS = (
    "@restcontroller",
    "@controller",
    "@service",
    "@kafkalistener",
    "@messagelistener",
    "resttemplate",
    "axios.",
    "fetch(",
    "httpclient",
    "jdbctemplate",
    "preparedstatement",
    "executeupdate",
    "queryforobject",
    "query(",
    "save(",
    "publish(",
    "produce(",
    "send(",
)


def extract_endpoints(path: Path, content: str) -> List[str]:
    endpoints: List[str] = []

    spring_endpoints = _extract_spring_endpoints(content)
    if spring_endpoints:
        endpoints.extend(spring_endpoints)

    dotnet_endpoints = _extract_dotnet_endpoints(content)
    if dotnet_endpoints:
        endpoints.extend(dotnet_endpoints)

    endpoints.extend(match.group(1) for match in FETCH_URL_RE.finditer(content))
    endpoints.extend(match.group(1) for match in AXIOS_URL_RE.finditer(content))
    endpoints.extend(route for _, route in APP_ROUTE_RE.findall(content))
    endpoints.extend(route for _, route in ROUTER_ROUTE_RE.findall(content))

    return _dedupe_preserve_order(endpoints)


def extract_payload_fields(content: str) -> List[str]:
    fields = [
        *KEY_VALUE_RE.findall(content),
        *JSON_KEY_RE.findall(content),
        *_extract_java_record_fields(content),
        *CSHARP_PROPERTY_RE.findall(content),
        *TS_FIELD_RE.findall(content),
        *_extract_method_style_fields(content),
    ]
    return _dedupe_preserve_order(field for field in fields if _looks_like_business_field(field))


def extract_system_of_record_paths(content: str, pii_matches: Sequence[PiiMatch]) -> List[str]:
    pii_tokens = {_normalize_field(match.attribute) for match in pii_matches}
    paths: List[str] = []
    for line in content.splitlines():
        lowered = line.lower()
        if any(word in lowered for word in ("select ", "insert ", "update ", "join ", "into ")):
            for token in SQL_COLUMN_RE.findall(lowered):
                normalized = _normalize_field(token)
                if normalized in pii_tokens or any(normalized in item for item in pii_tokens):
                    paths.append(token)
    return _dedupe_preserve_order(paths)


def extract_sensitive_table_map(content: str, pii_matches: Sequence[PiiMatch]) -> dict[str, List[str]]:
    columns = extract_system_of_record_paths(content, pii_matches)
    if not columns:
        return {}

    tables = [
        _clean_sql_identifier(match)
        for match in SQL_TABLE_RE.findall(content)
    ]
    tables = _dedupe_preserve_order(table for table in tables if table)
    return {table: list(columns) for table in tables}


def assess_ownership(
    path: Path,
    content: str,
    layer: str,
    endpoints: Sequence[str],
    payload_fields: Sequence[str],
    system_of_record_paths: Sequence[str],
    pii_matches: Sequence[PiiMatch],
    rest_calls: int,
    sql_count: int,
    jdbc_count: int,
    endpoint_count: int,
) -> OwnershipAssessment:
    rationale: List[str] = []
    matched_payload_fields = _dedupe_preserve_order(
        match.attribute
        for match in pii_matches
        if _normalize_field(match.attribute) in {_normalize_field(item) for item in payload_fields}
    )
    matched_endpoints = list(endpoints)
    likely_system_of_record_path = list(system_of_record_paths)
    supporting_model = _is_supporting_model_file(
        path,
        content,
        matched_endpoints,
        rest_calls,
        sql_count,
        jdbc_count,
        endpoint_count,
    )

    if supporting_model:
        rationale.append("File looks like a DTO/model/supporting type and not the primary implementation owner.")
        return OwnershipAssessment(
            likely_change_owner="supporting_model",
            ownership_confidence=0.61,
            role_in_flow="supporting_model",
            frontend_reference_only=False,
            backend_owner_confidence=0.18,
            jdbc_substitution_candidate=False,
            endpoint_correlation_score=0.0,
            matched_endpoints=matched_endpoints,
            matched_payload_fields=matched_payload_fields,
            likely_system_of_record_path=likely_system_of_record_path,
            related_files=[],
            rationale=rationale,
        )

    if layer.startswith("frontend"):
        role = "collects_and_sends" if rest_calls or endpoints else "display_only"
        confidence = 0.82 if rest_calls or endpoints else 0.72
        rationale.append(
            "Front-end classified file references sensitive fields but lacks direct data-access ownership."
        )
        if matched_endpoints:
            rationale.append("API call patterns suggest this file sends sensitive fields to another tier.")
        return OwnershipAssessment(
            likely_change_owner="frontend_reference_only",
            ownership_confidence=round(confidence, 2),
            role_in_flow=role,
            frontend_reference_only=True,
            backend_owner_confidence=0.12,
            jdbc_substitution_candidate=False,
            endpoint_correlation_score=0.0,
            matched_endpoints=matched_endpoints,
            matched_payload_fields=matched_payload_fields,
            likely_system_of_record_path=likely_system_of_record_path,
            related_files=[],
            rationale=rationale,
        )

    if layer in {"backend_with_data_access", "data_access"}:
        jdbc_candidate = jdbc_count > 0 or sql_count > 0
        role = "persists_or_publishes" if likely_system_of_record_path or sql_count else "receives_and_transforms"
        owner = "jdbc_candidate" if jdbc_candidate else "data_access_owner"
        confidence = 0.9 if jdbc_candidate else 0.82
        rationale.append("Back-end/data-access file contains direct SQL/JDBC or system-of-record indicators.")
        if matched_endpoints:
            rationale.append("This file also exposes or participates in an endpoint path.")
        return OwnershipAssessment(
            likely_change_owner=owner,
            ownership_confidence=round(confidence, 2),
            role_in_flow=role,
            frontend_reference_only=False,
            backend_owner_confidence=0.84,
            jdbc_substitution_candidate=jdbc_candidate,
            endpoint_correlation_score=0.0,
            matched_endpoints=matched_endpoints,
            matched_payload_fields=matched_payload_fields,
            likely_system_of_record_path=likely_system_of_record_path,
            related_files=[],
            rationale=rationale,
        )

    if layer == "backend":
        role = "receives_and_transforms" if endpoint_count or rest_calls else "protects_or_tokenizes"
        confidence = 0.84 if endpoint_count or rest_calls or matched_endpoints else 0.68
        rationale.append("Back-end service file appears to own business logic or transformation of sensitive fields.")
        if matched_endpoints:
            rationale.append("Route ownership suggests this file is a likely API-side change point.")
        return OwnershipAssessment(
            likely_change_owner="backend_logic_owner",
            ownership_confidence=round(confidence, 2),
            role_in_flow=role,
            frontend_reference_only=False,
            backend_owner_confidence=round(confidence, 2),
            jdbc_substitution_candidate=False,
            endpoint_correlation_score=0.0,
            matched_endpoints=matched_endpoints,
            matched_payload_fields=matched_payload_fields,
            likely_system_of_record_path=likely_system_of_record_path,
            related_files=[],
            rationale=rationale,
        )

    return OwnershipAssessment(
        likely_change_owner="unknown",
        ownership_confidence=0.35,
        role_in_flow="unknown",
        frontend_reference_only=False,
        backend_owner_confidence=0.35,
        jdbc_substitution_candidate=False,
        endpoint_correlation_score=0.0,
        matched_endpoints=matched_endpoints,
        matched_payload_fields=matched_payload_fields,
        likely_system_of_record_path=likely_system_of_record_path,
        related_files=[],
        rationale=["Insufficient ownership evidence from current heuristics."],
    )


def correlate_ownership(file_reports: Sequence[FileReport]) -> None:
    backend_route_candidates = [
        report
        for report in file_reports
        if report.ownership
        and report.ownership.likely_change_owner in {"backend_logic_owner", "jdbc_candidate", "data_access_owner"}
        and report.ownership.matched_endpoints
        and report.ownership.role_in_flow != "supporting_model"
    ]
    data_access_candidates = [
        report
        for report in file_reports
        if report.ownership
        and report.ownership.likely_change_owner in {"jdbc_candidate", "data_access_owner"}
        and report.ownership.role_in_flow != "supporting_model"
    ]

    for report in file_reports:
        if not report.ownership:
            continue
        if report.ownership.frontend_reference_only:
            _correlate_frontend_to_backend(report, backend_route_candidates)
        elif report.ownership.likely_change_owner == "backend_logic_owner":
            _correlate_backend_to_data_access(report, data_access_candidates)


def _correlate_frontend_to_backend(frontend_report: FileReport, backend_candidates: Sequence[FileReport]) -> None:
    frontend_paths = [_normalize_endpoint(item) for item in frontend_report.ownership.matched_endpoints]
    frontend_fields = {_normalize_field(item) for item in frontend_report.ownership.matched_payload_fields}

    best_matches: List[tuple[float, FileReport]] = []
    for backend_report in backend_candidates:
        backend_paths = [_normalize_endpoint(item) for item in backend_report.ownership.matched_endpoints]
        backend_fields = {_normalize_field(item) for item in backend_report.ownership.matched_payload_fields}
        path_score = _max_path_similarity(frontend_paths, backend_paths)
        field_score = _overlap_score(frontend_fields, backend_fields)
        score = round(path_score * 0.8 + field_score * 0.2, 2)
        if score >= 0.45:
            best_matches.append((score, backend_report))

    best_matches.sort(key=lambda item: item[0], reverse=True)
    if not best_matches:
        return

    frontend_report.ownership.backend_owner_confidence = round(best_matches[0][0], 2)
    frontend_report.ownership.endpoint_correlation_score = round(best_matches[0][0], 2)
    frontend_report.ownership.related_files = [match.path for _, match in best_matches[:3]]
    frontend_report.ownership.rationale.append(
        "Correlated front-end endpoints and payload fields with likely backend owner files."
    )

    for score, backend_report in best_matches[:3]:
        backend_report.ownership.related_files.append(frontend_report.path)
        backend_report.ownership.related_files = _dedupe_preserve_order(backend_report.ownership.related_files)
        backend_report.ownership.endpoint_correlation_score = max(
            backend_report.ownership.endpoint_correlation_score,
            round(score, 2),
        )
        backend_report.ownership.rationale.append(
            f"Correlated with front-end caller {frontend_report.path} using route/payload similarity."
        )


def _correlate_backend_to_data_access(backend_report: FileReport, data_access_candidates: Sequence[FileReport]) -> None:
    backend_fields = {_normalize_field(item) for item in backend_report.ownership.matched_payload_fields}
    if not backend_fields:
        backend_fields = {_normalize_field(match.attribute) for match in backend_report.pii_matches}

    best_matches: List[tuple[float, FileReport]] = []
    for data_report in data_access_candidates:
        if data_report.path == backend_report.path:
            continue
        data_fields = {
            _normalize_field(item)
            for item in (
                data_report.ownership.likely_system_of_record_path
                or data_report.ownership.matched_payload_fields
            )
        }
        if not data_fields:
            data_fields = {_normalize_field(match.attribute) for match in data_report.pii_matches}
        score = _overlap_score(backend_fields, data_fields)
        if score >= 0.35:
            best_matches.append((round(score, 2), data_report))

    best_matches.sort(key=lambda item: item[0], reverse=True)
    if not best_matches:
        return

    backend_report.ownership.related_files.extend(match.path for _, match in best_matches[:3])
    backend_report.ownership.related_files = _dedupe_preserve_order(backend_report.ownership.related_files)
    backend_report.ownership.rationale.append(
        "Correlated backend logic with likely data-access owner files using shared sensitive fields."
    )
    backend_report.ownership.endpoint_correlation_score = max(
        backend_report.ownership.endpoint_correlation_score,
        best_matches[0][0],
    )


def _extract_spring_endpoints(content: str) -> List[str]:
    class_position = _find_class_position(content)
    if class_position is None:
        return []

    header = content[:class_position]
    body = content[class_position:]

    base_paths = SPRING_REQUEST_MAPPING_VALUE_RE.findall(header) or [""]
    method_paths = SPRING_METHOD_MAPPING_RE.findall(body)
    endpoints: List[str] = []

    for method_path in method_paths:
        if not method_path.startswith("/"):
            method_path = f"/{method_path}"
        for base_path in base_paths:
            endpoints.append(_join_route(base_path, method_path))

    return _dedupe_preserve_order(endpoints)


def _extract_dotnet_endpoints(content: str) -> List[str]:
    class_position = _find_class_position(content)
    if class_position is None:
        return []

    header = content[:class_position]
    body = content[class_position:]

    base_paths = DOTNET_ROUTE_RE.findall(header) or [""]
    method_paths = DOTNET_HTTP_METHOD_RE.findall(body)
    endpoints: List[str] = []

    for method_path in method_paths:
        normalized_method_path = method_path.strip() if method_path else ""
        for base_path in base_paths:
            endpoints.append(_join_route(base_path, normalized_method_path))

    return _dedupe_preserve_order(endpoints)


def _extract_java_record_fields(content: str) -> List[str]:
    fields: List[str] = []
    for record_body in JAVA_RECORD_FIELD_RE.findall(content):
        fields.extend(JAVA_RECORD_ARG_RE.findall(record_body))
    return fields


def _extract_method_style_fields(content: str) -> List[str]:
    candidates: List[str] = []
    for field in JAVA_METHOD_CALL_FIELD_RE.findall(content):
        if field.startswith(("get", "set", "load", "save", "query", "post", "put", "update", "delete")):
            continue
        candidates.append(field)
    return candidates


def _find_class_position(content: str) -> int | None:
    match = CLASS_RE.search(content)
    return match.start() if match else None


def _join_route(base_path: str, method_path: str) -> str:
    left = base_path.strip() or ""
    right = method_path.strip() or ""
    if left and not left.startswith("/"):
        left = f"/{left}"
    if right and not right.startswith("/"):
        right = f"/{right}"
    return f"{left.rstrip('/')}{right}" if left else right


def _normalize_endpoint(endpoint: str) -> str:
    stripped = endpoint.strip()
    if "://" in stripped:
        parsed = urlparse(stripped)
        stripped = parsed.path or stripped
    stripped = re.sub(r"^(GET|POST|PUT|DELETE|PATCH)\s+", "", stripped, flags=re.IGNORECASE)
    stripped = re.sub(r"\{[^}]+\}", "{id}", stripped)
    stripped = re.sub(r":[A-Za-z_][A-Za-z0-9_]*", "{id}", stripped)
    stripped = re.sub(r"/\d+", "/{id}", stripped)
    stripped = re.sub(r"/[A-Za-z]+-\d+(?=/|$)", "/{id}", stripped)
    return stripped.lower()


def _normalize_field(field: str) -> str:
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", field).replace("-", "_").lower()


def _max_path_similarity(frontend_paths: Sequence[str], backend_paths: Sequence[str]) -> float:
    best = 0.0
    for left in frontend_paths:
        left_tokens = [token for token in left.split("/") if token]
        for right in backend_paths:
            right_tokens = [token for token in right.split("/") if token]
            if not left_tokens or not right_tokens:
                continue
            overlap = len(set(left_tokens) & set(right_tokens))
            union = len(set(left_tokens) | set(right_tokens))
            if union:
                best = max(best, overlap / union)
            if left == right:
                best = max(best, 1.0)
    return round(best, 2)


def _overlap_score(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    overlap = len(left & right)
    union = len(left | right)
    return round(overlap / union, 2) if union else 0.0


def _looks_like_business_field(field: str) -> bool:
    lowered = field.lower()
    return not lowered.startswith(
        (
            "http",
            "content",
            "method",
            "headers",
            "body",
            "json",
            "response",
            "request",
            "error",
        )
    )


def _is_supporting_model_file(
    path: Path,
    content: str,
    endpoints: Sequence[str],
    rest_calls: int,
    sql_count: int,
    jdbc_count: int,
    endpoint_count: int,
) -> bool:
    if endpoints or rest_calls or sql_count or jdbc_count or endpoint_count:
        return False

    stem = path.stem.lower()
    if any(token in stem for token in SUPPORTING_FILE_TOKENS):
        return True

    lowered = content.lower()
    if any(token in lowered for token in ORCHESTRATION_TOKENS):
        return False

    method_count = len(METHOD_RE.findall(content))
    return method_count <= 1


def _dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _clean_sql_identifier(identifier: str) -> str:
    return identifier.strip().strip(",);")
