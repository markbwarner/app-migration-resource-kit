from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Dict, Iterable, List, Set


SUPPORTED_EXTENSIONS: Set[str] = {
    ".py",
    ".java",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".cs",
    ".go",
    ".rb",
    ".php",
    ".sql",
    ".kt",
    ".kts",
    ".scala",
    ".yaml",
    ".yml",
    ".json",
    ".properties",
    ".xml",
    ".html",
    ".htm",
    ".jsp",
}


@dataclass(frozen=True)
class KeywordRule:
    category: str
    keywords: List[str]
    impact_hint: str


@dataclass(frozen=True)
class CustomKeywordRule:
    name: str
    category: str
    keywords: List[str]
    impact_hint: str


@dataclass(frozen=True)
class CustomRegexRule:
    name: str
    category: str
    pattern: str
    impact_hint: str


DEFAULT_PII_RULES: List[KeywordRule] = [
    KeywordRule("PERSON", ["first_name", "firstname", "last_name", "lastname", "full_name", "customer_name", "person_name", "employee_name"], "Personal name field"),
    KeywordRule("EMAIL_ADDRESS", ["email", "email_address", "customer_email", "work_email", "personal_email"], "Email address field"),
    KeywordRule("PHONE_NUMBER", ["phone", "mobile", "telephone", "cell"], "Phone number field"),
    KeywordRule("US_SSN", ["ssn", "social_security", "socialsecurity"], "US Social Security Number"),
    KeywordRule("DATE_OF_BIRTH", ["dob", "birth_date", "date_of_birth", "birthday"], "Date of birth"),
    KeywordRule("ADDRESS", ["address", "street_address", "home_address", "postal_code", "zipcode"], "Address data"),
    KeywordRule("CREDIT_CARD", ["credit_card", "card_number", "pan", "cvv"], "Payment card data"),
    KeywordRule("BANK_ACCOUNT", ["iban", "routing_number", "account_number", "bank_account"], "Bank account data"),
    KeywordRule("GOVERNMENT_ID", ["passport", "drivers_license", "license_number", "national_id"], "Government identifier"),
    KeywordRule("TAX_ID", ["tax_id", "tax_identifier", "tax_number"], "Tax identifier"),
    KeywordRule("HEALTH", ["diagnosis", "patient_id", "medical_record", "phi"], "Healthcare or PHI-related field"),
]


FRONTEND_HINTS: Dict[str, Iterable[str]] = {
    "frameworks": ["react", "angular", "vue", "redux", "@angular", "svelte"],
    "rest_clients": ["fetch(", "axios", "usequery", "graphql", "apollo"],
    "ui_terms": ["jsx", "tsx", "onclick", "ngoninit", "render("],
}

BACKEND_HINTS: Dict[str, Iterable[str]] = {
    "frameworks": ["springboot", "@restcontroller", "@controller", "@service", "@repository", "express(", "fastapi", "django", "flask", "@component"],
    "rest_endpoints": ["@getmapping", "@postmapping", "@requestmapping", "router.", "app.get(", "app.post("],
    "business_terms": ["service", "handler", "processor", "validator", "dto"],
}

DATA_ACCESS_HINTS: Dict[str, Iterable[str]] = {
    "jdbc": ["jdbctemplate", "drivermanager.getconnection", "datasource", "preparedstatement", "resultset", "jdbc:"],
    "orm": ["@entity", "@table", "@column", "hibernate", "jpa", "crudrepository"],
    "sql": ["select ", "insert ", "update ", "delete ", "join "],
    "messaging": ["kafka", "producerrecord", "consumerrecord", "@kafkalistener", "rabbitmq", "sqs", "sns"],
}


DEFAULT_EXCLUDES: Set[str] = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "target",
    "out",
    ".idea",
    ".vscode",
    "__pycache__",
}


def is_source_file(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def load_custom_rules(config_path: Path | None) -> tuple[List[CustomKeywordRule], List[CustomRegexRule]]:
    if config_path is None:
        return [], []

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    keyword_rules: List[CustomKeywordRule] = []
    for entry in raw.get("custom_patterns", []):
        keyword_rules.append(
            CustomKeywordRule(
                name=entry["name"],
                category=entry["category"],
                keywords=entry["keywords"],
                impact_hint=entry.get("impact_hint", f"Custom pattern: {entry['name']}"),
            )
        )
    regex_rules: List[CustomRegexRule] = []
    for entry in raw.get("custom_regex_patterns", []):
        regex_rules.append(
            CustomRegexRule(
                name=entry["name"],
                category=entry["category"],
                pattern=entry["pattern"],
                impact_hint=entry.get("impact_hint", f"Custom regex pattern: {entry['name']}"),
            )
        )
    return keyword_rules, regex_rules
