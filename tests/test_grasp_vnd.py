"""Test di GRASP multi-start e VND."""

from pathlib import Path

import pytest

from cmmoflp_nuclear_siting.core.instance import (
    CandidateSite,
    Community,
    ProblemInstance,
)
from cmmoflp_nuclear_siting.core.validation import validate_solution
from cmmoflp_nuclear_siting.heuristics.grasp_vnd import (
    GraspVndConfig,
    improve_with_vnd,
    solve_grasp_vnd,
)


TOY_PATH = Path("instances/test/toy_instance_01.json")


def build_two_swap_instance() -> ProblemInstance:
    """Crea un caso in cui nessun 1-swap migliora, ma il 2-swap sì."""

    return ProblemInstance(
        name="two_swap_instance",
        p=2,
        communities=[
            Community(
                id="c1",
                x=0.0,
                y=0.0,
                demand=1.0,
            )
        ],
        sites=[
            CandidateSite(
                id="s1",
                x=2.0,
                y=0.0,
                capacity=10.0,
            ),
            CandidateSite(
                id="s2",
                x=-2.0,
                y=0.0,
                capacity=10.0,
            ),
            CandidateSite(
                id="s3",
                x=10.0,
                y=0.0,
                capacity=10.0,
            ),
            CandidateSite(
                id="s4",
                x=-9.0,
                y=0.0,
                capacity=10.0,
            ),
        ],
    )


def test_grasp_vnd_returns_feasible_toy_solution() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)
    config = GraspVndConfig(
        random_seed=7,
        max_starts=10,
        time_limit_seconds=2.0,
    )

    solution = solve_grasp_vnd(instance, config)
    validation = validate_solution(instance, solution)

    assert validation.feasible
    assert solution.objective_value == pytest.approx(
        18.0277563773,
        abs=1e-6,
    )
    assert set(solution.open_sites) == {"s1", "s4"}


def test_grasp_vnd_is_reproducible_with_same_seed() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)
    config = GraspVndConfig(
        random_seed=123,
        max_starts=8,
        time_limit_seconds=2.0,
    )

    first = solve_grasp_vnd(instance, config)
    second = solve_grasp_vnd(instance, config)

    assert first.open_sites == second.open_sites
    assert first.objective_value == pytest.approx(
        second.objective_value,
        abs=1e-9,
    )


def test_targeted_two_swap_escapes_one_swap_local_minimum() -> None:
    instance = build_two_swap_instance()
    config = GraspVndConfig(
        max_starts=1,
        time_limit_seconds=2.0,
        candidate_list_size=4,
        secondary_open_limit=2,
    )

    solution = improve_with_vnd(
        instance,
        initial_sites=["s1", "s2"],
        config=config,
    )

    assert set(solution.open_sites) == {"s3", "s4"}
    assert solution.objective_value == pytest.approx(9.0)
    assert solution.metadata["two_swap_moves"] >= 1


def test_grasp_vnd_stops_when_upper_bound_is_reached() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)
    config = GraspVndConfig(
        random_seed=42,
        max_starts=100,
        time_limit_seconds=5.0,
    )

    solution = solve_grasp_vnd(instance, config)

    assert solution.metadata["upper_bound_reached"]
    assert solution.metadata["optimality_certified_by_upper_bound"]
    assert solution.metadata["starts_completed"] < 100
    assert solution.objective_value == pytest.approx(
        solution.metadata["objective_upper_bound"],
        abs=1e-9,
    )
