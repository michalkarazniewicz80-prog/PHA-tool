import pytest

from pha_tool import RiskBand, RiskMatrix


def test_scores_and_bands_default_matrix():
    matrix = RiskMatrix()

    assert matrix.score(5, 4) == 20
    assert matrix.band(1, 4) == RiskBand.LOW
    assert matrix.band(3, 3) == RiskBand.MEDIUM
    assert matrix.band(5, 2) == RiskBand.HIGH
    assert matrix.band(5, 5) == RiskBand.CRITICAL


def test_priority_orders_highest_risk_first():
    matrix = RiskMatrix()

    assert matrix.priority(5, 5) == 1
    assert matrix.priority(5, 3) == 2
    assert matrix.priority(3, 3) == 3
    assert matrix.priority(1, 1) == 4


def test_rating_validation():
    matrix = RiskMatrix()

    with pytest.raises(ValueError, match="severity must be between 1 and 5"):
        matrix.score(6, 1)
