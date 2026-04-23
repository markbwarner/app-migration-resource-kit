from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .config import load_custom_rules
from .reporting import (
    render_console_report,
    write_change_targets_csv,
    write_dba_planning_sql,
    write_file_reports_csv,
    write_json_file_reports,
    write_json_report,
    write_json_summary,
)
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
        "--csv-out",
        dest="csv_out",
        help="Optional path to write an Excel-friendly CSV of likely change targets.",
    )
    parser.add_argument(
        "--json-summary-out",
        dest="json_summary_out",
        help="Optional path to write a summary-only JSON report.",
    )
    parser.add_argument(
        "--json-file-reports-out",
        dest="json_file_reports_out",
        help="Optional path to write only the file_reports array as JSON.",
    )
    parser.add_argument(
        "--csv-file-reports-out",
        dest="csv_file_reports_out",
        help="Optional path to write a flattened CSV of all file-level reports.",
    )
    parser.add_argument(
        "--sql-out",
        dest="sql_out",
        help="Optional path to write DBA planning SQL for jdbc_candidate tables.",
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
        help="Include detailed file-by-file findings in JSON output. Console output stays summary-first by default.",
    )
    parser.add_argument(
        "--console-include-file-reports",
        action="store_true",
        help="Include detailed file-by-file findings in console output. Default console output shows only the executive summary.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    root_path = Path(args.path).resolve()

    if not root_path.exists() or not root_path.is_dir():
        parser.error(f"Path does not exist or is not a directory: {root_path}")

    json_output_path = Path(args.json_out).resolve() if args.json_out else None
    csv_output_path = Path(args.csv_out).resolve() if args.csv_out else None
    json_summary_output_path = Path(args.json_summary_out).resolve() if args.json_summary_out else None
    json_file_reports_output_path = (
        Path(args.json_file_reports_out).resolve() if args.json_file_reports_out else None
    )
    csv_file_reports_output_path = (
        Path(args.csv_file_reports_out).resolve() if args.csv_file_reports_out else None
    )
    sql_output_path = Path(args.sql_out).resolve() if args.sql_out else None

    custom_rules, custom_regex_rules = load_custom_rules(Path(args.custom_patterns).resolve()) if args.custom_patterns else ([], [])
    def emit_progress(message: str) -> None:
        print(message, file=sys.stderr)

    report = scan_directory(
        root_path,
        exclude_dirs=args.exclude_dir,
        exclude_paths=[
            path
            for path in (
                json_output_path,
                csv_output_path,
                json_summary_output_path,
                json_file_reports_output_path,
                csv_file_reports_output_path,
                sql_output_path,
            )
            if path
        ],
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
            include_file_reports=args.console_include_file_reports,
        )
    )

    if args.json_out:
        write_json_report(
            report,
            json_output_path,
            include_file_reports=args.include_file_reports,
        )
    if args.csv_out:
        write_change_targets_csv(report, csv_output_path)
    if args.json_summary_out:
        write_json_summary(report, json_summary_output_path)
    if args.json_file_reports_out:
        write_json_file_reports(report, json_file_reports_output_path)
    if args.csv_file_reports_out:
        write_file_reports_csv(report, csv_file_reports_output_path)
    if args.sql_out:
        write_dba_planning_sql(report, sql_output_path)

    return 0
