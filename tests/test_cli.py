import csv
import zipfile

from pha_tool.cli import main


def test_template_and_score_commands(tmp_path):
    template_path = tmp_path / "worksheet.csv"
    output_path = tmp_path / "scored.csv"

    assert main(["template", str(template_path)]) == 0

    with template_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "Reactor",
                "High temperature",
                "Cooling failure",
                "Overpressure",
                "Alarm; PSV",
                "5",
                "3",
                "Add trip",
                "Controls",
                "2026-12-31",
                "open",
            ]
        )

    assert main(["score", str(template_path), "--output", str(output_path)]) == 0

    with output_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert rows[0]["risk_score"] == "15"
    assert rows[0]["risk_band"] == "high"
    assert rows[0]["priority"] == "2"


def test_template_and_score_commands_write_excel_workbooks(tmp_path):
    template_path = tmp_path / "worksheet.xlsx"
    output_path = tmp_path / "scored.xlsx"

    assert main(["template", str(template_path)]) == 0
    assert template_path.read_bytes().startswith(b"PK")

    csv_path = tmp_path / "worksheet.csv"
    csv_path.write_text(
        "node,deviation,cause,consequence,safeguards,severity,likelihood,recommendation,owner,due_date,status\n"
        "Reactor,High temperature,Cooling failure,Overpressure,Alarm; PSV,5,3,"
        "Add trip,Controls,2026-12-31,open\n",
        encoding="utf-8",
    )

    assert main(["score", str(csv_path), "--output", str(output_path)]) == 0

    with zipfile.ZipFile(output_path) as workbook:
        assert "xl/worksheets/sheet1.xml" in workbook.namelist()
        sheet_xml = workbook.read("xl/worksheets/sheet1.xml").decode("utf-8")

    assert "risk_score" in sheet_xml
    assert "risk_band" in sheet_xml
    assert "high" in sheet_xml
