from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List

from .config import CustomKeywordRule, CustomRegexRule, DEFAULT_PII_RULES
from .models import PiiMatch


TOKEN_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _normalize_identifier(identifier: str) -> str:
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", identifier).lower()


def detect_keyword_matches(
    line_number: int,
    line: str,
    custom_rules: Iterable[CustomKeywordRule] | None = None,
    suppress_default_on_custom_match: bool = False,
) -> List[PiiMatch]:
    matches: List[PiiMatch] = []
    identifiers = {token: _normalize_identifier(token) for token in TOKEN_PATTERN.findall(line)}
    custom_rules = list(custom_rules or [])

    for original, normalized in identifiers.items():
        custom_matched = False
        custom_matches: List[PiiMatch] = []
        for rule in custom_rules:
            if _matches_keyword_rule(normalized, rule.keywords):
                custom_matched = True
                custom_matches.append(
                    PiiMatch(
                        line_number=line_number,
                        attribute=original,
                        category=rule.category,
                        detector="custom_keyword",
                        confidence=0.85,
                        impact_hint=rule.impact_hint,
                        pattern_name=rule.name,
                    )
                )

        if suppress_default_on_custom_match and custom_matched:
            matches.extend(custom_matches)
            continue

        for rule in DEFAULT_PII_RULES:
            if _matches_keyword_rule(normalized, rule.keywords):
                matches.append(
                    PiiMatch(
                        line_number=line_number,
                        attribute=original,
                        category=rule.category,
                        detector="keyword",
                        confidence=0.72,
                        impact_hint=rule.impact_hint,
                        pattern_name=None,
                    )
                )
                break
        matches.extend(custom_matches)

    return _dedupe_matches(matches)


def _matches_keyword_rule(normalized_identifier: str, keywords: Iterable[str]) -> bool:
    parts = [part for part in normalized_identifier.split("_") if part]
    joined_parts = "_".join(parts)
    for keyword in keywords:
        if joined_parts == keyword:
            return True
        if joined_parts.startswith(f"{keyword}_") or joined_parts.endswith(f"_{keyword}"):
            return True
        keyword_parts = keyword.split("_")
        if len(keyword_parts) > 1:
            for start in range(0, max(1, len(parts) - len(keyword_parts) + 1)):
                if parts[start : start + len(keyword_parts)] == keyword_parts:
                    return True
    return False


def detect_presidio_matches(line_number: int, line: str, analyzer) -> List[PiiMatch]:
    if analyzer is None or not line.strip():
        return []

    try:
        results = analyzer.analyze(text=line, language="en")
    except Exception:
        return []

    matches: List[PiiMatch] = []
    for result in results:
        snippet = line[result.start:result.end].strip() or "<literal>"
        matches.append(
            PiiMatch(
                line_number=line_number,
                attribute=snippet,
                category=result.entity_type,
                detector="presidio",
                confidence=round(result.score, 2),
                impact_hint="Literal or comment text recognized by Presidio",
                pattern_name=None,
            )
        )
    return _dedupe_matches(matches)


def detect_custom_regex_matches(
    line_number: int,
    line: str,
    regex_rules: Iterable[CustomRegexRule] | None = None,
) -> List[PiiMatch]:
    matches: List[PiiMatch] = []
    for rule in regex_rules or []:
        try:
            for regex_match in re.finditer(rule.pattern, line):
                snippet = regex_match.group(0)
                matches.append(
                    PiiMatch(
                        line_number=line_number,
                        attribute=snippet,
                        category=rule.category,
                        detector="custom_regex",
                        confidence=0.9,
                        impact_hint=rule.impact_hint,
                        pattern_name=rule.name,
                    )
                )
        except re.error:
            continue
    return _dedupe_matches(matches)


def _dedupe_matches(matches: Iterable[PiiMatch]) -> List[PiiMatch]:
    seen = set()
    deduped: List[PiiMatch] = []
    for match in matches:
        key = (match.line_number, match.attribute.lower(), match.category)
        if key not in seen:
            seen.add(key)
            deduped.append(match)
    return deduped


def build_presidio_analyzer():
    try:
        from presidio_analyzer import AnalyzerEngine
    except Exception:
        return None

    try:
        return AnalyzerEngine()
    except Exception:
        return None
