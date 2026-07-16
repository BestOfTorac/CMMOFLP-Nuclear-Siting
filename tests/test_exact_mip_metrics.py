"""Test delle metriche MIP restituite da AMPL."""

from pathlib import Path

import pytest

from cmmoflp_nuclear_siting.exact.ampl_runner import (
    extract_objective_name,
    parse_ampl_output,
)


def test_extract_objective_name(tmp_path: Path) -> None:
    model = tmp_path / "model.mod"
    model.write_text(
        """
var z;
maximize MaxSafety:
    z;
""",
        encoding="utf-8",
    )

    assert extract_objective_name(model) == "MaxSafety"


def test_parse_optimal_mip_metrics() -> None:
    output = """
CMMOFLP_RESULT|method=compact|status=solved|code=0|objective=18.0278|best_bound=18.0278|relative_mip_gap=0|absolute_mip_gap=0|solver_time=0.15
CMMOFLP_OPEN|s1|s4
"""

    result = parse_ampl_output(
        output,
        expected_method="compact",
        runtime_seconds=0.25,
    )

    assert result.feasible
    assert result.has_incumbent
    assert result.optimality_certified
    assert result.termination_reason == "optimal"
    assert result.best_bound == pytest.approx(18.0278)
    assert result.relative_mip_gap == pytest.approx(0.0)


def test_parse_time_limit_with_incumbent() -> None:
    output = """
CMMOFLP_RESULT|method=compact|status=limit|code=402|objective=16|best_bound=20|relative_mip_gap=0.25|absolute_mip_gap=4|solver_time=60
CMMOFLP_OPEN|s2|s6
"""

    result = parse_ampl_output(
        output,
        expected_method="compact",
        runtime_seconds=61.0,
    )

    assert result.feasible
    assert result.has_incumbent
    assert not result.optimality_certified
    assert result.termination_reason == "time_limit"
    assert result.objective_value == pytest.approx(16.0)
    assert result.best_bound == pytest.approx(20.0)
    assert result.relative_mip_gap == pytest.approx(0.25)


def test_parse_time_limit_without_incumbent() -> None:
    output = """
CMMOFLP_RESULT|method=compact|status=limit|code=401|objective=0|best_bound=20|relative_mip_gap=Infinity|absolute_mip_gap=Infinity|solver_time=60
CMMOFLP_OPEN
"""

    result = parse_ampl_output(
        output,
        expected_method="compact",
        runtime_seconds=61.0,
    )

    assert not result.feasible
    assert not result.has_incumbent
    assert not result.optimality_certified
    assert result.objective_value is None
    assert result.best_bound == pytest.approx(20.0)
