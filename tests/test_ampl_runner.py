"""Test dell'integrazione AMPL senza richiedere AMPL in CI."""

from pathlib import Path

import pytest

from cmmoflp_nuclear_siting.core.instance import ProblemInstance
from cmmoflp_nuclear_siting.exact.ampl_runner import (
    parse_ampl_output,
    write_ampl_data,
)


TOY_PATH = Path("instances/test/toy_instance_01.json")


def test_write_ampl_data_contains_core_sections(
    tmp_path: Path,
) -> None:
    instance = ProblemInstance.from_json(TOY_PATH)
    output_path = tmp_path / "toy.dat"

    write_ampl_data(instance, output_path)

    content = output_path.read_text(encoding="utf-8")

    assert "set COMMUNITIES := c1 c2 c3 c4 c5;" in content
    assert "set SITES := s1 s2 s3 s4;" in content
    assert "param p := 2;" in content
    assert "param demand :=" in content
    assert "param capacity :=" in content
    assert "param distance:" in content


def test_parse_compact_output() -> None:
    output = """
CMMOFLP_RESULT|method=compact|status=solved|code=0|objective=18.0278|solver_time=0.015
CMMOFLP_OPEN|s1|s4
"""

    result = parse_ampl_output(
        output,
        expected_method="compact",
        runtime_seconds=0.10,
    )

    assert result.status == "solved"
    assert result.feasible
    assert result.objective_value == pytest.approx(18.0278)
    assert result.solver_time_seconds == pytest.approx(0.015)
    assert result.open_sites == ("s1", "s4")


def test_parse_threshold_output() -> None:
    output = """
CMMOFLP_RESULT|method=threshold|status=solved|code=0|objective=18.0278|solver_time=0.021
CMMOFLP_OPEN|s1|s4
"""

    result = parse_ampl_output(
        output,
        expected_method="threshold",
        runtime_seconds=0.12,
    )

    assert result.method == "threshold"
    assert result.feasible
    assert result.open_sites == ("s1", "s4")


def test_parse_missing_marker_returns_error() -> None:
    result = parse_ampl_output(
        "AMPL execution failed",
        expected_method="compact",
        runtime_seconds=0.2,
    )

    assert result.status == "error"
    assert not result.feasible
    assert result.objective_value is None
