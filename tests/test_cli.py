import csv

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
