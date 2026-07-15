"""Test dell'analisi dei gap euristici."""

import pandas as pd
import pytest

from cmmoflp_nuclear_siting.analysis.gaps import (
    aggregate_gaps_by_class,
    build_heuristic_gap_table,
    summarize_heuristic_gaps,
)


def sample_exact() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "instance_id": "a",
                "method": "compact",
                "status": "solved",
                "feasible": True,
                "objective_value": 10.0,
                "runtime_seconds": 1.0,
                "open_sites": "s1;s2",
            },
            {
                "instance_id": "b",
                "method": "compact",
                "status": "solved",
                "feasible": True,
                "objective_value": 12.0,
                "runtime_seconds": 1.2,
                "open_sites": "s2;s3",
            },
        ]
    )


def sample_heuristics() -> pd.DataFrame:
    rows = []

    common_a = {
        "instance_id": "a",
        "class_id": "tiny_uniform_tight",
        "size": "tiny",
        "distribution": "uniform",
        "capacity_level": "tight",
        "seed": 1,
    }
    common_b = {
        "instance_id": "b",
        "class_id": "tiny_uniform_tight",
        "size": "tiny",
        "distribution": "uniform",
        "capacity_level": "tight",
        "seed": 2,
    }

    rows.extend(
        [
            {
                **common_a,
                "method": "greedy",
                "status": "success",
                "feasible": True,
                "objective_value": 9.0,
                "runtime_seconds": 0.01,
                "open_sites": "s1;s3",
            },
            {
                **common_b,
                "method": "greedy",
                "status": "error",
                "feasible": False,
                "objective_value": None,
                "runtime_seconds": 0.01,
                "open_sites": "",
            },
            {
                **common_a,
                "method": "local_search",
                "status": "success",
                "feasible": True,
                "objective_value": 10.0,
                "runtime_seconds": 0.02,
                "open_sites": "s1;s2",
            },
            {
                **common_b,
                "method": "local_search",
                "status": "success",
                "feasible": True,
                "objective_value": 11.0,
                "runtime_seconds": 0.02,
                "open_sites": "s2;s4",
            },
        ]
    )

    return pd.DataFrame(rows)


def test_gap_table_computes_maximization_gap() -> None:
    comparison = build_heuristic_gap_table(
        sample_heuristics(),
        sample_exact(),
    )

    greedy_a = comparison[
        (comparison["instance_id"] == "a")
        & (comparison["method"] == "greedy")
    ].iloc[0]

    assert greedy_a["gap_percent"] == pytest.approx(10.0)
    assert greedy_a["quality_status"] == "suboptimal"


def test_gap_table_classifies_optimal_and_failed_runs() -> None:
    comparison = build_heuristic_gap_table(
        sample_heuristics(),
        sample_exact(),
    )

    statuses = {
        (row.instance_id, row.method): row.quality_status
        for row in comparison.itertuples(index=False)
    }

    assert statuses[("a", "local_search")] == "optimal"
    assert statuses[("b", "greedy")] == "heuristic_failed"


def test_gap_summary_counts_quality_levels() -> None:
    comparison = build_heuristic_gap_table(
        sample_heuristics(),
        sample_exact(),
    )
    summary = summarize_heuristic_gaps(comparison)

    assert summary["greedy"]["runs"] == 2
    assert summary["greedy"]["failed_runs"] == 1
    assert summary["local_search"]["optimal_matches"] == 1
    assert summary["local_search"]["suboptimal_runs"] == 1


def test_gap_aggregation_groups_by_method() -> None:
    comparison = build_heuristic_gap_table(
        sample_heuristics(),
        sample_exact(),
    )
    aggregated = aggregate_gaps_by_class(comparison)

    assert len(aggregated) == 2
    assert set(aggregated["method"]) == {
        "greedy",
        "local_search",
    }
