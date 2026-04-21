from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .config import load_custom_rules
from .reporting import render_console_report, write_json_report
from .scanner import scan_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan source code for likely PII references and estimate CRDP migration impact."
    )
    parser.add_argument("path", help="Root directory to scan")
    parser.add_argument(
        "--json-out",
        dest="json_out",
        help="Optional path to write a JSON report",
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Directory name to exclude. Can be supplied multiple times.",
    )
    parser.add_argument(
        "--custom-patterns",
        dest="custom_patterns",
        help="Optional JSON file containing customer-defined search patterns.",
    )
    parser.add_argument(
        "--custom-patterns-override-defaults",
        action="store_true",
        help="When a custom pattern matches, suppress the built-in keyword category for that same identifier.",
    )
    parser.add_argument(
        "--use-presidio",
        action="store_true",
        help="Enable optional Presidio analysis for literals, comments, and sample payload text when Presidio is installed.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output during scanning.",
    )
    parser.add_argument(
        "--show-hint-breakdown",
        action="store_true",
        help="Show per-file matched hint terms and counts used for classification.",
    )
    parser.add_argument(
        "--include-file-reports",
        action="store_true",
        help="Include detailed file-by-file findings in console output. Default output shows only the executive summary.",
    )
    parser.add_argument(
        "--json-include-file-reports",
        action="store_true",
        help="Include detailed file-by-file findings in JSON output. Default JSON output contains the executive summary only.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    root_path = Path(args.path).resolve()

    if not root_path.exists() or not root_path.is_dir():
        parser.error(f"Path does not exist or is not a directory: {root_path}")

    custom_rules, custom_regex_rules = load_custom_rules(Path(args.custom_patterns).resolve()) if args.custom_patterns else ([], [])
    def emit_progress(message: str) -> None:
        print(message, file=sys.stderr)

    report = scan_directory(
        root_path,
        exclude_dirs=args.exclude_dir,
        custom_rules=custom_rules,
        custom_regex_rules=custom_regex_rules,
        suppress_default_on_custom_match=args.custom_patterns_override_defaults,
        use_presidio=args.use_presidio,
        progress_callback=None if args.quiet else emit_progress,
    )
    print(
        render_console_report(
            report,
            show_hint_breakdown=args.show_hint_breakdown,
            include_file_reports=args.include_file_reports,
        )
    )

    if args.json_out:
        write_json_report(
            report,
            Path(args.json_out).resolve(),
            include_file_reports=args.json_include_file_reports,
        )

    return 0
