"""Test dell'euristica greedy sulla toy instance."""

from pathlib import Path

import pytest

from cmmoflp_nuclear_siting.core.instance import ProblemInstance
from cmmoflp_nuclear_siting.core.validation import validate_solution
from cmmoflp_nuclear_siting.heuristics.greedy import solve_greedy


TOY_PATH = Path("instances/test/toy_instance_01.json")


def test_greedy_returns_feasible_solution() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)

    solution = solve_greedy(instance)
    validation = validate_solution(instance, solution)

    assert validation.feasible
    assert len(solution.open_sites) == instance.p
    assert set(solution.assignments) == {
        community.id for community in instance.communities
    }


def test_greedy_matches_toy_optimum() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)

    solution = solve_greedy(instance)

    assert solution.open_sites == ["s1", "s4"]
    assert solution.objective_value == pytest.approx(
        18.0277563773,
        abs=1e-6,
    )
