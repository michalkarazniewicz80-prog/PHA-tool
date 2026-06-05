# PHA Tool

PHA Tool is a lightweight Python toolkit for building and risk-ranking Process Hazard Analysis
(PHA) or HAZOP worksheets. It provides:

- A configurable 5x5 risk matrix.
- Data models for PHA worksheet rows and recommendations.
- CSV import/export for spreadsheet-friendly workflows.
- A small CLI for scoring worksheets and creating starter templates.

> Safety note: this tool is intended to support documentation and prioritization. It does not
> replace qualified engineering judgment, site procedures, regulatory requirements, or formal
> process safety reviews.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pha-tool template worksheet.csv
pha-tool template worksheet.xlsx
pha-tool score worksheet.csv --output scored.csv
pha-tool score worksheet.csv --output scored.xlsx
```

## Worksheet columns

The CSV and Excel interfaces use the following columns:

| Column | Description |
| --- | --- |
| `node` | Process node or system under review. |
| `deviation` | Deviation from intended operation. |
| `cause` | Credible initiating cause. |
| `consequence` | Potential consequence if safeguards fail. |
| `safeguards` | Existing safeguards or controls. |
| `severity` | Severity score from 1 to 5. |
| `likelihood` | Likelihood score from 1 to 5. |
| `recommendation` | Optional recommendation text. |
| `owner` | Optional action owner. |
| `due_date` | Optional due date. |
| `status` | Recommendation status. Defaults to `open`. |

When scoring a worksheet, PHA Tool appends `risk_score`, `risk_band`, and `priority` columns. Use an `.xlsx` output path to create a downloadable Excel workbook, or a `.csv` path for spreadsheet-friendly CSV output.

## Risk bands

The default matrix multiplies severity by likelihood and assigns bands:

- `low`: score 1-4
- `medium`: score 5-9
- `high`: score 10-16
- `critical`: score 17-25

## Development

```bash
python -m pytest
ruff check .
PYTHONPATH=src python -m pha_tool template /tmp/worksheet.xlsx
PYTHONPATH=src python -m pha_tool score docs/worksheet-example.csv --output /tmp/scored.xlsx
```
