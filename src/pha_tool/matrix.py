"""Risk matrix primitives for PHA worksheet scoring."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RiskBand(str, Enum):
    """Qualitative risk band assigned from a quantitative matrix score."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class RiskMatrix:
    """A severity-by-likelihood risk matrix.

    The default configuration uses a common 5x5 matrix. Severity and likelihood scores are
    integers from ``min_value`` to ``max_value``. The numeric risk score is their product, and
    qualitative bands are selected using inclusive upper thresholds.
    """

    min_value: int = 1
    max_value: int = 5
    medium_threshold: int = 5
    high_threshold: int = 10
    critical_threshold: int = 17

    def validate_rating(self, value: int, label: str) -> None:
        """Validate a severity or likelihood value.

        Args:
            value: Rating to validate.
            label: Human-readable field name for error messages.

        Raises:
            ValueError: If the value is outside the configured matrix range.
        """

        if value < self.min_value or value > self.max_value:
            raise ValueError(f"{label} must be between {self.min_value} and {self.max_value}")

    def score(self, severity: int, likelihood: int) -> int:
        """Return the numeric risk score for a severity/likelihood pair."""

        self.validate_rating(severity, "severity")
        self.validate_rating(likelihood, "likelihood")
        return severity * likelihood

    def band(self, severity: int, likelihood: int) -> RiskBand:
        """Return the qualitative risk band for a severity/likelihood pair."""

        risk_score = self.score(severity, likelihood)
        if risk_score >= self.critical_threshold:
            return RiskBand.CRITICAL
        if risk_score >= self.high_threshold:
            return RiskBand.HIGH
        if risk_score >= self.medium_threshold:
            return RiskBand.MEDIUM
        return RiskBand.LOW

    def priority(self, severity: int, likelihood: int) -> int:
        """Return an action priority where 1 is highest urgency."""

        band = self.band(severity, likelihood)
        priorities = {
            RiskBand.CRITICAL: 1,
            RiskBand.HIGH: 2,
            RiskBand.MEDIUM: 3,
            RiskBand.LOW: 4,
        }
        return priorities[band]
