"""Test della procedura di riparazione e della local search."""

from pathlib import Path

import pytest

from cmmoflp_nuclear_siting.core.instance import (
    CandidateSite,
    Community,
    ProblemInstance,
)
from cmmoflp_nuclear_siting.core.validation import validate_solution
from cmmoflp_nuclear_siting.heuristics.greedy import solve_greedy
from cmmoflp_nuclear_siting.heuristics.local_search import solve_local_search
from cmmoflp_nuclear_siting.heuristics.repair import find_feasible_assignment


TOY_PATH = Path("instances/test/toy_instance_01.json")


def build_repair_instance() -> ProblemInstance:
    """Crea un caso in cui il best-fit fallisce ma un assegnamento esiste."""

    return ProblemInstance(
        name="repair_instance",
        p=2,
        communities=[
            Community(id="c1", x=0.0, y=0.0, demand=4.0),
            Community(id="c2", x=1.0, y=0.0, demand=3.0),
            Community(id="c3", x=2.0, y=0.0, demand=2.0),
            Community(id="c4", x=3.0, y=0.0, demand=2.0),
        ],
        sites=[
            CandidateSite(id="s1", x=10.0, y=0.0, capacity=5.0),
            CandidateSite(id="s2", x=20.0, y=0.0, capacity=6.0),
        ],
        metadata={"purpose": "repair_test"},
    )


def test_local_search_preserves_toy_optimum() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)

    solution = solve_local_search(instance)
    validation = validate_solution(instance, solution)

    assert validation.feasible
    assert solution.open_sites == ["s1", "s4"]
    assert solution.objective_value == pytest.approx(
        18.0277563773,
        abs=1e-6,
    )


def test_repair_finds_assignment_when_best_fit_fails() -> None:
    instance = build_repair_instance()

    assignment = find_feasible_assignment(instance, ["s1", "s2"])

    assert assignment is not None

    loads = {"s1": 0.0, "s2": 0.0}
    demand = {
        community.id: community.demand
        for community in instance.communities
    }
    capacity = {
        site.id: site.capacity
        for site in instance.sites
    }

    for community_id, site_id in assignment.items():
        loads[site_id] += demand[community_id]

    assert loads["s1"] <= capacity["s1"]
    assert loads["s2"] <= capacity["s2"]


def test_local_search_repairs_a_failed_greedy_assignment() -> None:
    instance = build_repair_instance()

    with pytest.raises(ValueError):
        solve_greedy(instance)

    solution = solve_local_search(instance)
    validation = validate_solution(instance, solution)

    assert validation.feasible
    assert set(solution.open_sites) == {"s1", "s2"}
    assert set(solution.assignments) == {"c1", "c2", "c3", "c4"}
