from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PiiMatch:
    line_number: int
    attribute: str
    category: str
    detector: str
    confidence: float
    impact_hint: str
    pattern_name: str | None = None


@dataclass
class FileClassification:
    layer: str
    confidence: float
    reasons: List[str] = field(default_factory=list)


@dataclass
class ComplexityAssessment:
    score: float
    rating: str
    rationale: List[str] = field(default_factory=list)


@dataclass
class OwnershipAssessment:
    likely_change_owner: str
    ownership_confidence: float
    role_in_flow: str
    frontend_reference_only: bool
    backend_owner_confidence: float
    jdbc_substitution_candidate: bool
    endpoint_correlation_score: float = 0.0
    matched_endpoints: List[str] = field(default_factory=list)
    matched_payload_fields: List[str] = field(default_factory=list)
    likely_system_of_record_path: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)
    rationale: List[str] = field(default_factory=list)


@dataclass
class FileReport:
    path: str
    lines_of_code: int
    classification: FileClassification
    pii_matches: List[PiiMatch] = field(default_factory=list)
    summary_by_category: Dict[str, int] = field(default_factory=dict)
    jdbc_candidate_count: int = 0
    code_change_candidate_count: int = 0
    rest_call_count: int = 0
    sql_statement_count: int = 0
    endpoint_count: int = 0
    service_call_hint_count: int = 0
    backend_hint_count: int = 0
    integration_hint_count: int = 0
    service_call_hint_breakdown: Dict[str, int] = field(default_factory=dict)
    backend_hint_breakdown: Dict[str, int] = field(default_factory=dict)
    integration_hint_breakdown: Dict[str, int] = field(default_factory=dict)
    sensitive_tables: Dict[str, List[str]] = field(default_factory=dict)
    ownership: Optional[OwnershipAssessment] = None
    complexity: Optional[ComplexityAssessment] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class ScanReport:
    root_path: str
    files_scanned: int
    files_with_pii: int
    total_pii_matches: int
    file_reports: List[FileReport] = field(default_factory=list)
    totals_by_category: Dict[str, int] = field(default_factory=dict)
    tables_summary: Dict[str, Dict[str, List[str] | int]] = field(default_factory=dict)
    jdbc_candidate_total: int = 0
    code_change_candidate_total: int = 0
