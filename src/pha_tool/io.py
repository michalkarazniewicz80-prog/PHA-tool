"""CSV input and output helpers for PHA worksheets."""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path

from pha_tool.worksheet import SCORED_FIELDS, WORKSHEET_FIELDS, WorksheetRow


def read_worksheet(path: Path) -> list[WorksheetRow]:
    """Read worksheet rows from a CSV file."""

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = sorted(set(WORKSHEET_FIELDS) - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"worksheet is missing required columns: {', '.join(missing)}")
        return [WorksheetRow.from_dict(row) for row in reader]


def write_template(path: Path) -> None:
    """Write an empty worksheet template CSV."""

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=WORKSHEET_FIELDS)
        writer.writeheader()


def write_scored_rows(path: Path, rows: Iterable[dict[str, str | int]]) -> None:
    """Write scored worksheet rows to a CSV file."""

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SCORED_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
