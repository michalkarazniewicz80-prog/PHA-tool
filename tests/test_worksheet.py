from pha_tool.worksheet import WorksheetRow, score_rows


def test_worksheet_row_from_dict_defaults_status():
    row = WorksheetRow.from_dict(
        {
            "node": " Reactor ",
            "deviation": "High pressure",
            "cause": "Blocked outlet",
            "consequence": "Relief event",
            "safeguards": "PSV",
            "severity": "5",
            "likelihood": "2",
            "recommendation": "Review PSV sizing",
            "owner": "PSE",
            "due_date": "2026-09-30",
            "status": "",
        }
    )

    assert row.node == "Reactor"
    assert row.recommendation.status == "open"


def test_score_rows_adds_risk_fields():
    row = WorksheetRow.from_dict(
        {
            "node": "Reactor",
            "deviation": "No cooling",
            "cause": "Cooling water failure",
            "consequence": "Runaway reaction",
            "safeguards": "Temperature alarm",
            "severity": "5",
            "likelihood": "4",
            "recommendation": "Add interlock",
            "owner": "Controls",
            "due_date": "2026-10-31",
            "status": "open",
        }
    )

    scored = score_rows([row])[0]

    assert scored["risk_score"] == 20
    assert scored["risk_band"] == "critical"
    assert scored["priority"] == 1
