from pathlib import Path

from cmmoflp_nuclear_siting.core.instance import ProblemInstance
from cmmoflp_nuclear_siting.core.solution import Solution
from cmmoflp_nuclear_siting.core.validation import validate_solution

TOY_PATH = Path("instances/test/toy_instance_01.json")


def test_feasible_solution_is_accepted() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)
    solution = Solution(
        open_sites=["s2", "s4"],
        assignments={"c1": "s2", "c2": "s2", "c3": "s2", "c4": "s4", "c5": "s4"},
    )
    result = validate_solution(instance, solution)
    assert result.feasible
    assert result.objective_value is not None


def test_assignment_to_closed_site_is_rejected() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)
    solution = Solution(
        open_sites=["s2", "s4"],
        assignments={"c1": "s1", "c2": "s2", "c3": "s2", "c4": "s4", "c5": "s4"},
    )
    result = validate_solution(instance, solution)
    assert not result.feasible
