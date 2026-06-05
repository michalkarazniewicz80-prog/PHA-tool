"""PHA worksheet row models and CSV serialization helpers."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from pha_tool.matrix import RiskBand, RiskMatrix

WORKSHEET_FIELDS = [
    "node",
    "deviation",
    "cause",
    "consequence",
    "safeguards",
    "severity",
    "likelihood",
    "recommendation",
    "owner",
    "due_date",
    "status",
]
SCORED_FIELDS = [*WORKSHEET_FIELDS, "risk_score", "risk_band", "priority"]


@dataclass(frozen=True)
class Recommendation:
    """A recommendation or action item arising from a PHA worksheet row."""

    text: str = ""
    owner: str = ""
    due_date: str = ""
    status: str = "open"


@dataclass(frozen=True)
class WorksheetRow:
    """A single PHA worksheet scenario."""

    node: str
    deviation: str
    cause: str
    consequence: str
    safeguards: str
    severity: int
    likelihood: int
    recommendation: Recommendation = field(default_factory=Recommendation)

    @classmethod
    def from_dict(cls, row: dict[str, str]) -> WorksheetRow:
        """Create a worksheet row from a CSV dictionary."""

        return cls(
            node=row.get("node", "").strip(),
            deviation=row.get("deviation", "").strip(),
            cause=row.get("cause", "").strip(),
            consequence=row.get("consequence", "").strip(),
            safeguards=row.get("safeguards", "").strip(),
            severity=_parse_rating(row.get("severity", ""), "severity"),
            likelihood=_parse_rating(row.get("likelihood", ""), "likelihood"),
            recommendation=Recommendation(
                text=row.get("recommendation", "").strip(),
                owner=row.get("owner", "").strip(),
                due_date=row.get("due_date", "").strip(),
                status=(row.get("status", "") or "open").strip(),
            ),
        )

    def to_dict(self) -> dict[str, str | int]:
        """Serialize the worksheet row to a CSV-friendly dictionary."""

        return {
            "node": self.node,
            "deviation": self.deviation,
            "cause": self.cause,
            "consequence": self.consequence,
            "safeguards": self.safeguards,
            "severity": self.severity,
            "likelihood": self.likelihood,
            "recommendation": self.recommendation.text,
            "owner": self.recommendation.owner,
            "due_date": self.recommendation.due_date,
            "status": self.recommendation.status,
        }

    def scored_dict(self, matrix: RiskMatrix | None = None) -> dict[str, str | int | RiskBand]:
        """Serialize the row with risk score, risk band, and priority columns."""

        active_matrix = matrix or RiskMatrix()
        risk_band = active_matrix.band(self.severity, self.likelihood)
        return {
            **self.to_dict(),
            "risk_score": active_matrix.score(self.severity, self.likelihood),
            "risk_band": risk_band.value,
            "priority": active_matrix.priority(self.severity, self.likelihood),
        }


def score_rows(
    rows: Iterable[WorksheetRow], matrix: RiskMatrix | None = None
) -> list[dict[str, str | int | RiskBand]]:
    """Score worksheet rows and return dictionaries suitable for CSV output."""

    active_matrix = matrix or RiskMatrix()
    return [row.scored_dict(active_matrix) for row in rows]


def _parse_rating(value: str, label: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be an integer") from exc
