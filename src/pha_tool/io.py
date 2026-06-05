"""CSV and Excel input/output helpers for PHA worksheets."""

# ruff: noqa: E501

from __future__ import annotations

import csv
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from pha_tool.worksheet import SCORED_FIELDS, WORKSHEET_FIELDS, WorksheetRow

EXCEL_SUFFIXES = {".xlsx"}


def read_worksheet(path: Path) -> list[WorksheetRow]:
    """Read worksheet rows from a CSV file."""

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = sorted(set(WORKSHEET_FIELDS) - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"worksheet is missing required columns: {', '.join(missing)}")
        return [WorksheetRow.from_dict(row) for row in reader]


def write_template(path: Path) -> None:
    """Write an empty worksheet template as CSV or XLSX based on the file suffix."""

    if _is_excel_path(path):
        write_excel_workbook(path, [], WORKSHEET_FIELDS, sheet_name="PHA Template")
        return

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=WORKSHEET_FIELDS)
        writer.writeheader()


def write_scored_rows(path: Path, rows: Iterable[dict[str, str | int]]) -> None:
    """Write scored worksheet rows as CSV or XLSX based on the file suffix."""

    materialized_rows = list(rows)
    if _is_excel_path(path):
        write_excel_workbook(path, materialized_rows, SCORED_FIELDS, sheet_name="PHA Scores")
        return

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SCORED_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(materialized_rows)


def write_excel_workbook(
    path: Path,
    rows: Iterable[dict[str, str | int]],
    fieldnames: Sequence[str],
    *,
    sheet_name: str,
) -> None:
    """Write rows to a dependency-free Office Open XML workbook.

    The generated ``.xlsx`` file is intentionally small and uses inline strings so the project can
    produce downloadable Excel workbooks without requiring optional spreadsheet dependencies.
    """

    materialized_rows = list(rows)
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as workbook:
        workbook.writestr("[Content_Types].xml", _content_types_xml())
        workbook.writestr("_rels/.rels", _package_relationships_xml())
        workbook.writestr("xl/workbook.xml", _workbook_xml(sheet_name))
        workbook.writestr("xl/_rels/workbook.xml.rels", _workbook_relationships_xml())
        workbook.writestr("xl/styles.xml", _styles_xml())
        workbook.writestr("xl/worksheets/sheet1.xml", _worksheet_xml(fieldnames, materialized_rows))
        workbook.writestr("docProps/core.xml", _core_properties_xml())
        workbook.writestr("docProps/app.xml", _app_properties_xml())


def _is_excel_path(path: Path) -> bool:
    return path.suffix.lower() in EXCEL_SUFFIXES


def _worksheet_xml(fieldnames: Sequence[str], rows: list[dict[str, str | int]]) -> str:
    all_rows: list[Sequence[str | int]] = [fieldnames]
    all_rows.extend([tuple(row.get(field, "") for field in fieldnames) for row in rows])
    dimensions = f"A1:{_column_name(len(fieldnames))}{max(len(all_rows), 1)}"
    xml_rows = "".join(_row_xml(index, values) for index, values in enumerate(all_rows, start=1))
    column_widths = "".join(
        f'<col min="{index}" max="{index}" width="{_column_width(field)}" customWidth="1"/>'
        for index, field in enumerate(fieldnames, start=1)
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <dimension ref="{dimensions}"/>
  <sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/><selection pane="bottomLeft" activeCell="A2" sqref="A2"/></sheetView></sheetViews>
  <cols>{column_widths}</cols>
  <sheetData>{xml_rows}</sheetData>
  <autoFilter ref="{dimensions}"/>
</worksheet>'''


def _row_xml(row_number: int, values: Sequence[str | int]) -> str:
    cells = "".join(_cell_xml(row_number, column_index, value) for column_index, value in enumerate(values, 1))
    return f'<row r="{row_number}">{cells}</row>'


def _cell_xml(row_number: int, column_index: int, value: str | int) -> str:
    reference = f"{_column_name(column_index)}{row_number}"
    style = ' s="1"' if row_number == 1 else ""
    if isinstance(value, int):
        return f'<c r="{reference}"{style}><v>{value}</v></c>'
    return f'<c r="{reference}" t="inlineStr"{style}><is><t>{escape(str(value))}</t></is></c>'


def _column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def _column_width(field: str) -> int:
    widths = {
        "node": 18,
        "deviation": 22,
        "cause": 28,
        "consequence": 34,
        "safeguards": 34,
        "recommendation": 34,
        "owner": 18,
        "due_date": 14,
        "status": 14,
        "risk_band": 14,
    }
    return widths.get(field, max(len(field) + 2, 12))


def _content_types_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''


def _package_relationships_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''


def _workbook_xml(sheet_name: str) -> str:
    escaped_name = escape(sheet_name[:31])
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="{escaped_name}" sheetId="1" r:id="rId1"/></sheets>
</workbook>'''


def _workbook_relationships_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''


def _styles_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs>
</styleSheet>'''


def _core_properties_xml() -> str:
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:creator>PHA Tool</dc:creator>
  <cp:lastModifiedBy>PHA Tool</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:modified>
</cp:coreProperties>'''


def _app_properties_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>PHA Tool</Application>
</Properties>'''
