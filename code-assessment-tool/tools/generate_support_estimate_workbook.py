from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


OUTPUT_PATH = Path("docs/assessment/crdp-support-effort-estimator.xlsx")


@dataclass
class Cell:
    value: str | int | float | None = None
    kind: str = "str"
    style: int = 0


def col_letter(index: int) -> str:
    letters = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def inline_string_cell(ref: str, value: str, style: int = 0) -> str:
    safe = escape(value)
    style_attr = f' s="{style}"' if style else ""
    return f'<c r="{ref}" t="inlineStr"{style_attr}><is><t>{safe}</t></is></c>'


def number_cell(ref: str, value: int | float, style: int = 0) -> str:
    style_attr = f' s="{style}"' if style else ""
    return f'<c r="{ref}"{style_attr}><v>{value}</v></c>'


def formula_cell(ref: str, formula: str, style: int = 0) -> str:
    style_attr = f' s="{style}"' if style else ""
    safe_formula = escape(formula)
    return f'<c r="{ref}"{style_attr}><f>{safe_formula}</f></c>'


def build_row_xml(row_number: int, cells: list[Cell]) -> str:
    parts: list[str] = [f'<row r="{row_number}">']
    for column_index, cell in enumerate(cells, start=1):
        if cell is None:
            continue
        if cell.value is None:
            continue
        ref = f"{col_letter(column_index)}{row_number}"
        if cell.kind == "formula":
            parts.append(formula_cell(ref, str(cell.value), cell.style))
        elif cell.kind == "num":
            parts.append(number_cell(ref, cell.value, cell.style))
        else:
            parts.append(inline_string_cell(ref, str(cell.value), cell.style))
    parts.append("</row>")
    return "".join(parts)


def worksheet_xml(rows: list[list[Cell]], column_widths: list[int] | None = None) -> str:
    cols_xml = ""
    if column_widths:
        pieces = ["<cols>"]
        for index, width in enumerate(column_widths, start=1):
            pieces.append(
                f'<col min="{index}" max="{index}" width="{width}" customWidth="1"/>'
            )
        pieces.append("</cols>")
        cols_xml = "".join(pieces)

    row_xml = "".join(build_row_xml(i, row) for i, row in enumerate(rows, start=1))
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
        '<sheetFormatPr defaultRowHeight="15"/>'
        f"{cols_xml}"
        f"<sheetData>{row_xml}</sheetData>"
        "</worksheet>"
    )


def workbook_xml(sheet_names: Iterable[str]) -> str:
    sheets = []
    for sheet_id, name in enumerate(sheet_names, start=1):
        safe_name = escape(name)
        sheets.append(
            f'<sheet name="{safe_name}" sheetId="{sheet_id}" '
            f'r:id="rId{sheet_id}"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        "<bookViews><workbookView/></bookViews>"
        f"<sheets>{''.join(sheets)}</sheets>"
        "</workbook>"
    )


def workbook_rels_xml(sheet_count: int) -> str:
    relationships = []
    for index in range(1, sheet_count + 1):
        relationships.append(
            '<Relationship '
            f'Id="rId{index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
        )
    relationships.append(
        '<Relationship Id="rId{0}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'.format(sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{''.join(relationships)}"
        "</Relationships>"
    )


def root_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )


def content_types_xml(sheet_count: int) -> str:
    overrides = [
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/xl/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
    ]
    for index in range(1, sheet_count + 1):
        overrides.append(
            f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f"{''.join(overrides)}"
        "</Types>"
    )


def styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="2">'
        '<font><sz val="11"/><color theme="1"/><name val="Calibri"/><family val="2"/></font>'
        '<font><b/><sz val="11"/><color theme="1"/><name val="Calibri"/><family val="2"/></font>'
        "</fonts>"
        '<fills count="2">'
        '<fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill>'
        "</fills>"
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="2">'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
        "</cellXfs>"
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        "</styleSheet>"
    )


def cell(value: str | int | float | None = None, kind: str = "str", style: int = 0) -> Cell:
    return Cell(value=value, kind=kind, style=style)


def instructions_sheet() -> list[list[Cell]]:
    return [
        [cell("CRDP Support Effort Estimator", style=1)],
        [cell("Purpose", style=1)],
        [
            cell(
                "Use this workbook to compare monthly and annual incremental support effort for tokenization capability "
                "across different application portfolio sizes and rollout assumptions."
            )
        ],
        [
            cell(
                "The calculation used on the scenario tabs is: Support Effort = Base Complexity x Readiness Multiplier "
                "x Criticality Multiplier x Data/Performance Multiplier."
            )
        ],
        [cell("How to use it", style=1)],
        [cell("1. Review or edit the multiplier tables on the Assumptions and Conservative_Assumptions tabs.")],
        [cell("2. On each Scenario tab, adjust application counts and dropdown-style labels directly in the cells.")],
        [cell("3. Base complexity hours are sample midpoint assumptions from the estimating guide.")],
        [cell("4. The 250-app scenario is intentionally broad and may overstate scope before the assessment tool narrows true change owners.")],
        [cell("5. The 100-app and 50-app scenarios model what support can look like after assessment-based scope reduction.")],
        [cell("6. Portfolio_Summary compares baseline and conservative assumptions side by side.")],
        [cell("7. Role_Breakdown allocates monthly hours across roles such as DevOps, DBA, Thales admin, and application support.")],
        [cell("8. Visual_Summary provides chart-like bars using formulas so the workbook stays self-contained.")],
        [cell("Scenario design intent", style=1)],
        [cell("Scenario_250 = broad pre-assessment estate view")],
        [cell("Scenario_100 = likely in-scope portfolio after ownership analysis")],
        [cell("Scenario_50 = focused rollout wave or narrowed true-change-owner population")],
        [cell("FTE note", style=1)],
        [cell("Monthly FTE is calculated using 160 hours per month as a planning assumption.")],
    ]


def assumptions_sheet(title: str, readiness_values: tuple[float, float, float], criticality_values: tuple[float, float, float], data_values: tuple[float, float, float], notes: list[str]) -> list[list[Cell]]:
    return [
        [cell(title, style=1)],
        [],
        [cell("Base Complexity"), cell("Hours / App / Month", style=1), None, cell("Readiness"), cell("Multiplier", style=1), None, cell("Criticality"), cell("Multiplier", style=1), None, cell("Data / Performance"), cell("Multiplier", style=1)],
        [cell("Low"), cell(3, kind="num"), None, cell("High"), cell(readiness_values[0], kind="num"), None, cell("BusinessHours"), cell(criticality_values[0], kind="num"), None, cell("Low"), cell(data_values[0], kind="num")],
        [cell("Medium"), cell(9.5, kind="num"), None, cell("Medium"), cell(readiness_values[1], kind="num"), None, cell("Near24x7"), cell(criticality_values[1], kind="num"), None, cell("Moderate"), cell(data_values[1], kind="num")],
        [cell("High"), cell(24, kind="num"), None, cell("Low"), cell(readiness_values[2], kind="num"), None, cell("HighlyCritical"), cell(criticality_values[2], kind="num"), None, cell("High"), cell(data_values[2], kind="num")],
        [],
        [cell("Notes", style=1)],
        *[[cell(note)] for note in notes],
    ]


def scenario_rows(
    name: str,
    rows: list[tuple[str, int, str, str, str, str, str]],
    assumptions_sheet_name: str = "Assumptions",
) -> list[list[Cell]]:
    sheet_rows: list[list[Cell]] = [
        [cell(f"{name} Support Effort Scenario", style=1)],
        [cell("Sample assumptions. Edit counts or multiplier labels as needed.")],
        [
            cell("Use Case", style=1),
            cell("Application Count", style=1),
            cell("Complexity", style=1),
            cell("Base Complexity Hours / App / Month", style=1),
            cell("Readiness", style=1),
            cell("Readiness Multiplier", style=1),
            cell("Criticality", style=1),
            cell("Criticality Multiplier", style=1),
            cell("Data / Performance", style=1),
            cell("Data / Performance Multiplier", style=1),
            cell("Adjusted Monthly Hours / App", style=1),
            cell("Total Monthly Hours", style=1),
            cell("Notes", style=1),
        ],
    ]

    start_row = 4
    for offset, (use_case, app_count, complexity, readiness, criticality, data_perf, note) in enumerate(rows):
        row_index = start_row + offset
        sheet_rows.append(
            [
                cell(use_case),
                cell(app_count, kind="num"),
                cell(complexity),
                cell(f"VLOOKUP(C{row_index},{assumptions_sheet_name}!$A$4:$B$6,2,FALSE)", kind="formula"),
                cell(readiness),
                cell(f"VLOOKUP(E{row_index},{assumptions_sheet_name}!$D$4:$E$6,2,FALSE)", kind="formula"),
                cell(criticality),
                cell(f"VLOOKUP(G{row_index},{assumptions_sheet_name}!$G$4:$H$6,2,FALSE)", kind="formula"),
                cell(data_perf),
                cell(f"VLOOKUP(I{row_index},{assumptions_sheet_name}!$J$4:$K$6,2,FALSE)", kind="formula"),
                cell(f'D{row_index}*F{row_index}*H{row_index}*J{row_index}', kind="formula"),
                cell(f'B{row_index}*K{row_index}', kind="formula"),
                cell(note),
            ]
        )

    summary_row = start_row + len(rows) + 1
    sheet_rows.extend(
        [
            [],
            [cell("Total applications", style=1), cell(f"SUM(B{start_row}:B{summary_row-2})", kind="formula")],
            [cell("Total monthly hours", style=1), cell(f"SUM(L{start_row}:L{summary_row-2})", kind="formula")],
            [cell("Total annual hours", style=1), cell(f"B{summary_row+1}*12", kind="formula")],
            [cell("Estimated monthly FTE (160h)", style=1), cell(f"B{summary_row+1}/160", kind="formula")],
        ]
    )
    return sheet_rows


def portfolio_summary_sheet() -> list[list[Cell]]:
    return [
        [cell("Portfolio Scenario Summary", style=1)],
        [cell("These totals roll up the scenario tabs and show how scope reduction changes support assumptions.")],
        [
            cell("Scenario", style=1),
            cell("Applications", style=1),
            cell("Baseline Monthly Hours", style=1),
            cell("Baseline Annual Hours", style=1),
            cell("Baseline Monthly FTE", style=1),
            cell("Conservative Monthly Hours", style=1),
            cell("Conservative Annual Hours", style=1),
            cell("Conservative Monthly FTE", style=1),
            cell("Interpretation", style=1),
        ],
        [
            cell("250 apps"),
            cell("Scenario_250!B12", kind="formula"),
            cell("Scenario_250!B13", kind="formula"),
            cell("Scenario_250!B14", kind="formula"),
            cell("Scenario_250!B15", kind="formula"),
            cell("Scenario_250_Conservative!B13", kind="formula"),
            cell("Scenario_250_Conservative!B14", kind="formula"),
            cell("Scenario_250_Conservative!B15", kind="formula"),
            cell("Broad pre-assessment estate view. Likely overstates true change-owner scope."),
        ],
        [
            cell("100 apps"),
            cell("Scenario_100!B12", kind="formula"),
            cell("Scenario_100!B13", kind="formula"),
            cell("Scenario_100!B14", kind="formula"),
            cell("Scenario_100!B15", kind="formula"),
            cell("Scenario_100_Conservative!B13", kind="formula"),
            cell("Scenario_100_Conservative!B14", kind="formula"),
            cell("Scenario_100_Conservative!B15", kind="formula"),
            cell("Post-assessment view where front-end-only references and low-impact apps are reduced."),
        ],
        [
            cell("50 apps"),
            cell("Scenario_50!B12", kind="formula"),
            cell("Scenario_50!B13", kind="formula"),
            cell("Scenario_50!B14", kind="formula"),
            cell("Scenario_50!B15", kind="formula"),
            cell("Scenario_50_Conservative!B13", kind="formula"),
            cell("Scenario_50_Conservative!B14", kind="formula"),
            cell("Scenario_50_Conservative!B15", kind="formula"),
            cell("Focused rollout wave or narrowed set of true back-end/data-access owners."),
        ],
    ]


def role_breakdown_sheet() -> list[list[Cell]]:
    rows = [
        [cell("Role-Based Monthly Effort Allocation", style=1)],
        [cell("Percentages are editable planning allocations applied to the baseline monthly scenario totals.")],
        [
            cell("Role", style=1),
            cell("Allocation %", style=1),
            cell("250 Apps Monthly Hours", style=1),
            cell("100 Apps Monthly Hours", style=1),
            cell("50 Apps Monthly Hours", style=1),
            cell("Role Description", style=1),
        ],
        [cell("Application developers / integration engineers"), cell(0.18, kind="num"), cell("Portfolio_Summary!C4*B4", kind="formula"), cell("Portfolio_Summary!C5*B4", kind="formula"), cell("Portfolio_Summary!C6*B4", kind="formula"), cell("Back-end change owners, wrappers, break-fix, vendor coordination")],
        [cell("DevOps / SRE"), cell(0.27, kind="num"), cell("Portfolio_Summary!C4*B5", kind="formula"), cell("Portfolio_Summary!C5*B5", kind="formula"), cell("Portfolio_Summary!C6*B5", kind="formula"), cell("AKS operations, observability, certificates, scaling, platform support")],
        [cell("Thales security administration"), cell(0.10, kind="num"), cell("Portfolio_Summary!C4*B6", kind="formula"), cell("Portfolio_Summary!C5*B6", kind="formula"), cell("Portfolio_Summary!C6*B6", kind="formula"), cell("Policies, user sets, audit review, key lifecycle oversight")],
        [cell("DBA / data engineering"), cell(0.15, kind="num"), cell("Portfolio_Summary!C4*B7", kind="formula"), cell("Portfolio_Summary!C5*B7", kind="formula"), cell("Portfolio_Summary!C6*B7", kind="formula"), cell("Protected tables, data-load planning, schema validation, SQL review")],
        [cell("Cloud architects / platform engineering"), cell(0.08, kind="num"), cell("Portfolio_Summary!C4*B8", kind="formula"), cell("Portfolio_Summary!C5*B8", kind="formula"), cell("Portfolio_Summary!C6*B8", kind="formula"), cell("Cluster topology, network design, workload placement guidance")],
        [cell("Performance / capacity engineering"), cell(0.10, kind="num"), cell("Portfolio_Summary!C4*B9", kind="formula"), cell("Portfolio_Summary!C5*B9", kind="formula"), cell("Portfolio_Summary!C6*B9", kind="formula"), cell("Prometheus review, reveal-heavy tuning, autoscaling thresholds")],
        [cell("Service management / release coordination"), cell(0.07, kind="num"), cell("Portfolio_Summary!C4*B10", kind="formula"), cell("Portfolio_Summary!C5*B10", kind="formula"), cell("Portfolio_Summary!C6*B10", kind="formula"), cell("Incidents, releases, change windows, escalation tracking")],
        [cell("Databricks / analytics specialists"), cell(0.05, kind="num"), cell("Portfolio_Summary!C4*B11", kind="formula"), cell("Portfolio_Summary!C5*B11", kind="formula"), cell("Portfolio_Summary!C6*B11", kind="formula"), cell("Batch UDFs, analytics reveal flows, downstream data consumers")],
        [],
        [cell("Allocation total", style=1), cell("SUM(B4:B11)", kind="formula", style=1)],
    ]
    return rows


def visual_summary_sheet() -> list[list[Cell]]:
    return [
        [cell("Visual Summary", style=1)],
        [cell("Formula-based bars provide a simple chart-like view without requiring external libraries.")],
        [cell("Scenario", style=1), cell("Baseline Monthly Hours", style=1), cell("Baseline Bar", style=1), cell("Conservative Monthly Hours", style=1), cell("Conservative Bar", style=1), cell("Baseline FTE", style=1), cell("Conservative FTE", style=1)],
        [cell("250 apps"), cell("Portfolio_Summary!C4", kind="formula"), cell('REPT("|",ROUND(B4/120,0))', kind="formula"), cell("Portfolio_Summary!F4", kind="formula"), cell('REPT("|",ROUND(D4/120,0))', kind="formula"), cell("Portfolio_Summary!E4", kind="formula"), cell("Portfolio_Summary!H4", kind="formula")],
        [cell("100 apps"), cell("Portfolio_Summary!C5", kind="formula"), cell('REPT("|",ROUND(B5/120,0))', kind="formula"), cell("Portfolio_Summary!F5", kind="formula"), cell('REPT("|",ROUND(D5/120,0))', kind="formula"), cell("Portfolio_Summary!E5", kind="formula"), cell("Portfolio_Summary!H5", kind="formula")],
        [cell("50 apps"), cell("Portfolio_Summary!C6", kind="formula"), cell('REPT("|",ROUND(B6/120,0))', kind="formula"), cell("Portfolio_Summary!F6", kind="formula"), cell('REPT("|",ROUND(D6/120,0))', kind="formula"), cell("Portfolio_Summary!E6", kind="formula"), cell("Portfolio_Summary!H6", kind="formula")],
    ]


def build_workbook() -> dict[str, str]:
    scenario_250 = [
        (
            "Front-end reference / proxy review",
            150,
            "Low",
            "Medium",
            "BusinessHours",
            "Low",
            "Many may only reference sensitive fields; assessment often removes most from true change scope.",
        ),
        (
            "Back-end API owners",
            30,
            "Medium",
            "Medium",
            "Near24x7",
            "Moderate",
            "Primary REST and service owners after assessment.",
        ),
        (
            "JDBC candidate applications",
            20,
            "Low",
            "High",
            "BusinessHours",
            "Moderate",
            "Lower incremental support if driver-based coverage is feasible.",
        ),
        (
            "Kafka producers / consumers",
            10,
            "High",
            "Medium",
            "HighlyCritical",
            "High",
            "Message-contract, replay, and reveal/protect troubleshooting sensitivity.",
        ),
        (
            "Mainframe / WebSphere / Oracle",
            10,
            "High",
            "Low",
            "HighlyCritical",
            "High",
            "Cross-platform support and contractor-readiness risk.",
        ),
        (
            "Databricks reveal / batch",
            20,
            "Medium",
            "Medium",
            "BusinessHours",
            "High",
            "Batch windows and downstream analytics dependencies.",
        ),
        (
            "Analytics / reveal-heavy",
            10,
            "High",
            "Medium",
            "Near24x7",
            "High",
            "Large result sets and performance sensitivity.",
        ),
    ]

    scenario_100 = [
        (
            "Front-end reference / proxy review",
            20,
            "Low",
            "Medium",
            "BusinessHours",
            "Low",
            "Reduced scope after ownership analysis.",
        ),
        (
            "Back-end API owners",
            25,
            "Medium",
            "Medium",
            "Near24x7",
            "Moderate",
            "Likely true REST and business-logic change owners.",
        ),
        (
            "JDBC candidate applications",
            15,
            "Low",
            "High",
            "BusinessHours",
            "Moderate",
            "Lower app-support burden if driver strategy is used.",
        ),
        (
            "Kafka producers / consumers",
            10,
            "High",
            "Medium",
            "HighlyCritical",
            "High",
            "Shared integration support required.",
        ),
        (
            "Mainframe / WebSphere / Oracle",
            10,
            "High",
            "Low",
            "HighlyCritical",
            "High",
            "Older middleware and cross-team coordination risk.",
        ),
        (
            "Databricks reveal / batch",
            10,
            "Medium",
            "Medium",
            "BusinessHours",
            "High",
            "Batch and data anomaly support.",
        ),
        (
            "Analytics / reveal-heavy",
            10,
            "High",
            "Medium",
            "Near24x7",
            "High",
            "Reveal-heavy performance review.",
        ),
    ]

    scenario_50 = [
        (
            "Front-end reference / proxy review",
            5,
            "Low",
            "Medium",
            "BusinessHours",
            "Low",
            "Small residual population after assessment and rollout prioritization.",
        ),
        (
            "Back-end API owners",
            15,
            "Medium",
            "Medium",
            "Near24x7",
            "Moderate",
            "Primary wave of back-end owners.",
        ),
        (
            "JDBC candidate applications",
            10,
            "Low",
            "High",
            "BusinessHours",
            "Moderate",
            "Targeted lower-impact rollout group.",
        ),
        (
            "Kafka producers / consumers",
            5,
            "High",
            "Medium",
            "HighlyCritical",
            "High",
            "Event-driven use case wave.",
        ),
        (
            "Mainframe / WebSphere / Oracle",
            5,
            "High",
            "Low",
            "HighlyCritical",
            "High",
            "High-touch legacy integration subset.",
        ),
        (
            "Databricks reveal / batch",
            5,
            "Medium",
            "Medium",
            "BusinessHours",
            "High",
            "Batch-focused rollout slice.",
        ),
        (
            "Analytics / reveal-heavy",
            5,
            "High",
            "Medium",
            "Near24x7",
            "High",
            "Performance-sensitive reveal subset.",
        ),
    ]

    sheets = {
        "Instructions": worksheet_xml(
            instructions_sheet(),
            column_widths=[28, 120],
        ),
        "Assumptions": worksheet_xml(
            assumptions_sheet(
                "Assumption Tables",
                readiness_values=(0.95, 1.10, 1.50),
                criticality_values=(1.0, 1.3, 1.6),
                data_values=(1.0, 1.2, 1.5),
                notes=[
                    "Low / Medium / High base complexity hours are midpoint planning assumptions derived from the estimating guide.",
                    "You can change any multiplier in this sheet and all baseline scenario totals will recalculate when the workbook is opened in Excel.",
                    "For front-end reference-only populations, the assessment tool often reduces the true support scope substantially.",
                ],
            ),
            column_widths=[22, 18, 4, 18, 12, 4, 18, 12, 4, 20, 12],
        ),
        "Conservative_Assumptions": worksheet_xml(
            assumptions_sheet(
                "Conservative Assumption Tables",
                readiness_values=(0.90, 1.00, 1.25),
                criticality_values=(1.0, 1.15, 1.35),
                data_values=(1.0, 1.10, 1.25),
                notes=[
                    "This tab models a lighter steady-state support assumption after reusable wrappers, good automation, and stable platform operations are in place.",
                    "These multipliers are useful for customer conversations where Thales policy administration and application break-fix are expected to remain low after onboarding.",
                    "Use this set when you want to show an efficiency-oriented operating model alongside the baseline view.",
                ],
            ),
            column_widths=[22, 18, 4, 18, 12, 4, 18, 12, 4, 20, 12],
        ),
        "Portfolio_Summary": worksheet_xml(
            portfolio_summary_sheet(),
            column_widths=[18, 16, 20, 20, 18, 22, 22, 20, 72],
        ),
        "Scenario_250": worksheet_xml(
            scenario_rows("250 Application", scenario_250),
            column_widths=[32, 16, 12, 26, 14, 18, 16, 18, 18, 22, 22, 18, 62],
        ),
        "Scenario_100": worksheet_xml(
            scenario_rows("100 Application", scenario_100),
            column_widths=[32, 16, 12, 26, 14, 18, 16, 18, 18, 22, 22, 18, 62],
        ),
        "Scenario_50": worksheet_xml(
            scenario_rows("50 Application", scenario_50),
            column_widths=[32, 16, 12, 26, 14, 18, 16, 18, 18, 22, 22, 18, 62],
        ),
        "Scenario_250_Conservative": worksheet_xml(
            scenario_rows("250 Application Conservative", scenario_250, assumptions_sheet_name="Conservative_Assumptions"),
            column_widths=[32, 16, 12, 26, 14, 18, 16, 18, 18, 22, 22, 18, 62],
        ),
        "Scenario_100_Conservative": worksheet_xml(
            scenario_rows("100 Application Conservative", scenario_100, assumptions_sheet_name="Conservative_Assumptions"),
            column_widths=[32, 16, 12, 26, 14, 18, 16, 18, 18, 22, 22, 18, 62],
        ),
        "Scenario_50_Conservative": worksheet_xml(
            scenario_rows("50 Application Conservative", scenario_50, assumptions_sheet_name="Conservative_Assumptions"),
            column_widths=[32, 16, 12, 26, 14, 18, 16, 18, 18, 22, 22, 18, 62],
        ),
        "Role_Breakdown": worksheet_xml(
            role_breakdown_sheet(),
            column_widths=[34, 14, 22, 22, 22, 70],
        ),
        "Visual_Summary": worksheet_xml(
            visual_summary_sheet(),
            column_widths=[18, 18, 36, 22, 36, 14, 16],
        ),
    }
    return sheets


def write_workbook(path: Path) -> None:
    sheets = build_workbook()
    sheet_names = list(sheets.keys())

    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as workbook:
        workbook.writestr("[Content_Types].xml", content_types_xml(len(sheet_names)))
        workbook.writestr("_rels/.rels", root_rels_xml())
        workbook.writestr("xl/workbook.xml", workbook_xml(sheet_names))
        workbook.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml(len(sheet_names)))
        workbook.writestr("xl/styles.xml", styles_xml())
        for index, sheet_name in enumerate(sheet_names, start=1):
            workbook.writestr(f"xl/worksheets/sheet{index}.xml", sheets[sheet_name])


if __name__ == "__main__":
    write_workbook(OUTPUT_PATH)
    print(f"Wrote workbook to {OUTPUT_PATH.resolve()}")
