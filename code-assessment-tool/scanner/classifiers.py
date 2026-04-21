from __future__ import annotations

from pathlib import Path
from collections import Counter
from typing import Dict, Iterable, Tuple

from .config import BACKEND_HINTS, DATA_ACCESS_HINTS, FRONTEND_HINTS
from .models import FileClassification


def _count_hits(content: str, patterns: Iterable[str]) -> int:
    lowered = content.lower()
    return sum(lowered.count(pattern.lower()) for pattern in patterns)


def _count_hits_breakdown(content: str, patterns: Iterable[str]) -> Dict[str, int]:
    lowered = content.lower()
    counts = Counter()
    for pattern in patterns:
        count = lowered.count(pattern.lower())
        if count:
            counts[pattern] += count
    return dict(counts)


def classify_file(path: Path, content: str) -> FileClassification:
    suffix = path.suffix.lower()
    frontend_score = 0
    backend_score = 0
    data_score = 0
    reasons = []

    if suffix in {".js", ".jsx", ".ts", ".tsx", ".html", ".htm"}:
        frontend_score += 2
        reasons.append(f"{suffix} extension is commonly used for front-end code")
    if suffix in {".java", ".kt", ".kts", ".cs", ".go", ".py", ".rb", ".php", ".jsp"}:
        backend_score += 2
        reasons.append(f"{suffix} extension is commonly used for back-end code")
    if suffix in {".sql", ".properties", ".xml"}:
        data_score += 2
        reasons.append(f"{suffix} extension is commonly used in data-access or configuration layers")

    frontend_hits = sum(_count_hits(content, values) for values in FRONTEND_HINTS.values())
    backend_hits = sum(_count_hits(content, values) for values in BACKEND_HINTS.values())
    data_hits = sum(_count_hits(content, values) for values in DATA_ACCESS_HINTS.values())
    frontend_score += frontend_hits
    backend_score += backend_hits
    data_score += data_hits

    if frontend_hits:
        reasons.append(f"Found {frontend_hits} front-end markers")
    if backend_hits:
        reasons.append(f"Found {backend_hits} back-end markers")
    if data_hits:
        reasons.append(f"Found {data_hits} data-access or integration markers")

    ranked = sorted(
        [
            ("frontend", frontend_score),
            ("backend", backend_score),
            ("data_access", data_score),
        ],
        key=lambda item: item[1],
        reverse=True,
    )

    top_label, top_score = ranked[0]
    second_score = ranked[1][1]
    if top_score == 0:
        return FileClassification(layer="unknown", confidence=0.2, reasons=["No strong framework or layer markers found"])

    if top_label == "frontend" and data_score > 0:
        layer = "frontend_with_service_calls"
    elif top_label == "backend" and data_score > 0:
        layer = "backend_with_data_access"
    else:
        layer = top_label

    confidence = min(0.95, 0.5 + (top_score - second_score) * 0.08 + top_score * 0.02)
    return FileClassification(layer=layer, confidence=round(confidence, 2), reasons=reasons[:5])


def analyze_hint_breakdowns(content: str) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, int]]:
    frontend_breakdown: Dict[str, int] = {}
    backend_breakdown: Dict[str, int] = {}
    data_breakdown: Dict[str, int] = {}

    for values in FRONTEND_HINTS.values():
        for pattern, count in _count_hits_breakdown(content, values).items():
            frontend_breakdown[pattern] = frontend_breakdown.get(pattern, 0) + count
    for values in BACKEND_HINTS.values():
        for pattern, count in _count_hits_breakdown(content, values).items():
            backend_breakdown[pattern] = backend_breakdown.get(pattern, 0) + count
    for values in DATA_ACCESS_HINTS.values():
        for pattern, count in _count_hits_breakdown(content, values).items():
            data_breakdown[pattern] = data_breakdown.get(pattern, 0) + count

    return frontend_breakdown, backend_breakdown, data_breakdown


def count_integration_markers(content: str) -> Tuple[int, int, int, int]:
    lowered = content.lower()
    rest_calls = sum(lowered.count(token) for token in ["fetch(", "axios", "resttemplate", "webclient", "httpclient", "requests.", "graphql", "apollo"])
    sql_count = sum(lowered.count(token) for token in ["select ", "insert ", "update ", "delete ", "preparedstatement", "jdbctemplate", "jdbc:"])
    endpoint_count = sum(lowered.count(token) for token in ["@getmapping", "@postmapping", "@requestmapping", "app.get(", "app.post(", "router.get(", "router.post("])
    jdbc_count = sum(lowered.count(token) for token in ["jdbctemplate", "drivermanager.getconnection", "datasource", "preparedstatement", "jdbc:", "resultset"])
    return rest_calls, sql_count, endpoint_count, jdbc_count
