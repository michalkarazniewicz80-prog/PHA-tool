# PHA Tool

PHA Tool is now a standalone browser-based Process Hazard Analysis (PHA/HAZOP) worksheet. Open `index.html` directly in a browser; no Python runtime, package installation, web server, or build step is required.

The HTML version provides:

- Navigation-driven screens so setup, nodes, worksheet, safeguards, actions, and dashboard views appear one at a time instead of stacked on one page, with export/import controls kept in the persistent top toolbar.
- A configurable-feeling worksheet flow for PHA scenarios.
- Clear, high-contrast dropdowns for severity, likelihood, and action status.
- Automatic 5x5 risk scoring with low, medium, high, and critical bands.
- Separate action tracker and dashboard pop-up windows for focused review.
- Process and environmental consequence rows are created as paired worksheet entries, each with its own risk-rating dropdowns.
- A live summary of scenario counts, risk bands, and open actions.
- An action tracker that rebuilds automatically from non-closed recommendations.
- CSV import, scored CSV export, and native .xlsx formatted Excel export with wrapped text plus fixed column widths and row heights for spreadsheet-friendly workflows.
- Local browser storage so worksheet entries persist between sessions on the same device.

> Safety note: this tool is intended to support documentation and prioritization. It does not replace qualified engineering judgment, site procedures, regulatory requirements, or formal process safety reviews.

## Quick start

1. Open `index.html` in a modern browser.
2. Add or edit worksheet scenarios.
3. Use severity and likelihood dropdowns to calculate risk automatically.
4. Add recommendation text, owner, due date, and status to populate the action tracker.
5. Export a scored CSV when you need a spreadsheet copy.

## Worksheet columns

The CSV interface uses the following columns:

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

When exporting a worksheet, PHA Tool appends `risk_score`, `risk_band`, and `priority` columns.

## Risk bands

The default matrix multiplies severity by likelihood and assigns bands:

- `low`: score 1-4
- `medium`: score 5-9
- `high`: score 10-16
- `critical`: score 17-25
