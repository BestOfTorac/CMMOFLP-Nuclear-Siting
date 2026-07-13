from pathlib import Path

from cmmoflp_nuclear_siting.core.instance import ProblemInstance

TOY_PATH = Path("instances/test/toy_instance_01.json")


def test_toy_instance_is_valid() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)
    assert instance.name == "toy_instance_01"
    assert instance.p == 2
    assert len(instance.communities) == 5
    assert len(instance.sites) == 4


def test_distance_matrix_has_expected_shape() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)
    matrix = instance.distance_matrix()
    assert len(matrix) == 5
    assert all(len(row) == 4 for row in matrix.values())
