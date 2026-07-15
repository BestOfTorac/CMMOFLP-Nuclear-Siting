"""Test della pipeline multi-seed GRASP-VND."""

from pathlib import Path

import pytest

from cmmoflp_nuclear_siting.core.instance import ProblemInstance
from cmmoflp_nuclear_siting.experiments.grasp_vnd_runner import (
    run_grasp_vnd_once,
)
from cmmoflp_nuclear_siting.heuristics.grasp_vnd import (
    GraspVndConfig,
)


TOY_PATH = Path("instances/test/toy_instance_01.json")


def test_grasp_vnd_runner_returns_normalized_result() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)
    result = run_grasp_vnd_once(
        instance=instance,
        algorithm_seed=42,
        config_template=GraspVndConfig(
            max_starts=10,
            time_limit_seconds=2.0,
        ),
    )

    assert result.status == "success"
    assert result.feasible
    assert result.objective_value == pytest.approx(
        18.0277563773,
        abs=1e-6,
    )
    assert result.algorithm_seed == 42
    assert result.method == "grasp_vnd"


def test_grasp_vnd_runner_records_upper_bound_certificate() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)
    result = run_grasp_vnd_once(
        instance=instance,
        algorithm_seed=123,
        config_template=GraspVndConfig(
            max_starts=100,
            time_limit_seconds=2.0,
        ),
    )

    assert result.upper_bound_reached
    assert result.optimality_certified_by_upper_bound
    assert result.starts_completed < 100
