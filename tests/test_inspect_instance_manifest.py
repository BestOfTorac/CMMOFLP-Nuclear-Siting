"""Test delle stime strutturali dei benchmark."""

import pytest

from cmmoflp_nuclear_siting.analysis.instance_complexity import (
    estimate_compact_complexity,
)


def test_medium_complexity_estimate() -> None:
    result = estimate_compact_complexity(
        instance_id="medium_uniform_tight_001",
        class_id="medium_uniform_tight",
        size="medium",
        communities=100,
        candidate_sites=30,
        plants_to_open=5,
    )

    assert result.binary_variables == 3030
    assert result.continuous_variables == 1
    assert result.constraints == 3161
    assert result.threshold_solves == 30


def test_large_complexity_estimate() -> None:
    result = estimate_compact_complexity(
        instance_id="large_clustered_loose_001",
        class_id="large_clustered_loose",
        size="large",
        communities=300,
        candidate_sites=75,
        plants_to_open=10,
    )

    assert result.binary_variables == 22575
    assert result.constraints == 22951
    assert result.threshold_solves == 75


def test_invalid_number_of_plants_is_rejected() -> None:
    with pytest.raises(ValueError):
        estimate_compact_complexity(
            instance_id="invalid",
            class_id="invalid",
            size="invalid",
            communities=10,
            candidate_sites=4,
            plants_to_open=5,
        )
