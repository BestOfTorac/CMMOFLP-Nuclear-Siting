"""Test dell'analisi dei metodi esatti."""

import pandas as pd
import pytest

from cmmoflp_nuclear_siting.analysis.exact import (
    aggregate_exact_by_class,
    build_exact_comparison,
    summarize_exact_comparison,
)


def sample_exact_results() -> pd.DataFrame:
    rows = []

    for instance_id, objective, compact_time, threshold_time in [
        ("a", 10.0, 0.2, 0.8),
        ("b", 12.0, 0.3, 1.5),
    ]:
        common = {
            "instance_id": instance_id,
            "class_id": "tiny_uniform_tight",
            "size": "tiny",
            "distribution": "uniform",
            "capacity_level": "tight",
            "seed": 1,
            "status": "solved",
            "feasible": True,
            "objective_value": objective,
            "open_sites": "s1;s2",
        }

        rows.append(
            {
                **common,
                "method": "compact",
                "runtime_seconds": compact_time,
                "solver_time_seconds": compact_time / 2,
            }
        )
        rows.append(
            {
                **common,
                "method": "threshold",
                "runtime_seconds": threshold_time,
                "solver_time_seconds": threshold_time / 2,
            }
        )

    return pd.DataFrame(rows)


def test_exact_comparison_detects_equivalent_solutions() -> None:
    comparison = build_exact_comparison(sample_exact_results())

    assert comparison["same_objective"].all()
    assert comparison["same_open_sites"].all()
    assert comparison["both_solved"].all()


def test_exact_summary_computes_runtime_ratio() -> None:
    dataframe = sample_exact_results()
    comparison = build_exact_comparison(dataframe)
    summary = summarize_exact_comparison(dataframe, comparison)

    assert summary["instances"] == 2
    assert summary["same_objective"] == 2
    assert summary["average_runtime_ratio"] == pytest.approx(4.5)


def test_exact_aggregation_groups_by_method() -> None:
    summary = aggregate_exact_by_class(sample_exact_results())

    assert len(summary) == 2
    assert set(summary["method"]) == {"compact", "threshold"}
    assert summary["solved"].sum() == 4
