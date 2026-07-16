"""Test dei criteri di arresto e della deadline globale."""

from pathlib import Path
from time import perf_counter

import pytest

from cmmoflp_nuclear_siting.core.instance import (
    CandidateSite,
    Community,
    ProblemInstance,
)
from cmmoflp_nuclear_siting.heuristics.grasp_vnd import (
    GraspVndConfig,
    solve_grasp_vnd,
)
from cmmoflp_nuclear_siting.heuristics.repair import (
    find_feasible_assignment,
)


TOY_PATH = Path("instances/test/toy_instance_01.json")


def build_capacity_blocked_instance() -> ProblemInstance:
    """Crea un caso in cui l'upper bound ignora capacità decisive."""

    return ProblemInstance(
        name="capacity_blocked",
        p=2,
        communities=[
            Community(
                id="c1",
                x=0.0,
                y=0.0,
                demand=10.0,
            ),
            Community(
                id="c2",
                x=0.0,
                y=0.0,
                demand=10.0,
            ),
        ],
        sites=[
            CandidateSite(
                id="s1",
                x=10.0,
                y=0.0,
                capacity=1.0,
            ),
            CandidateSite(
                id="s2",
                x=9.0,
                y=0.0,
                capacity=1.0,
            ),
            CandidateSite(
                id="s3",
                x=8.0,
                y=0.0,
                capacity=10.0,
            ),
            CandidateSite(
                id="s4",
                x=7.0,
                y=0.0,
                capacity=10.0,
            ),
        ],
    )


def test_repair_rejects_an_expired_deadline() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)

    with pytest.raises(TimeoutError):
        find_feasible_assignment(
            instance,
            open_sites=["s1", "s4"],
            deadline=perf_counter() - 1.0,
        )


def test_grasp_vnd_stops_after_stagnation() -> None:
    instance = build_capacity_blocked_instance()
    solution = solve_grasp_vnd(
        instance,
        GraspVndConfig(
            max_starts=100,
            max_starts_without_improvement=3,
            time_limit_seconds=5.0,
            candidate_list_size=4,
        ),
    )

    assert solution.objective_value == pytest.approx(7.0)
    assert not solution.metadata["upper_bound_reached"]
    assert solution.metadata["stop_reason"] == "stagnation"
    assert solution.metadata["stagnation_stops"] == 1
    assert solution.metadata["starts_completed"] <= 4


def test_zero_stagnation_limit_is_rejected() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)

    with pytest.raises(ValueError):
        solve_grasp_vnd(
            instance,
            GraspVndConfig(
                max_starts_without_improvement=0,
            ),
        )
