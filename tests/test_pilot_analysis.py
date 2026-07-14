"""Test dell'analisi pilota."""

import pandas as pd
import pytest

from cmmoflp_nuclear_siting.analysis.pilot import (
    aggregate_by_class,
    build_pairwise_comparison,
    summarize_pairwise,
)


def sample_results() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "instance_id": "a",
                "class_id": "tiny_tight",
                "size": "tiny",
                "distribution": "uniform",
                "capacity_level": "tight",
                "seed": 1,
                "method": "greedy",
                "status": "error",
                "feasible": False,
                "objective_value": None,
                "runtime_seconds": 0.1,
                "error": "failed",
            },
            {
                "instance_id": "a",
                "class_id": "tiny_tight",
                "size": "tiny",
                "distribution": "uniform",
                "capacity_level": "tight",
                "seed": 1,
                "method": "local_search",
                "status": "success",
                "feasible": True,
                "objective_value": 10.0,
                "runtime_seconds": 0.2,
                "error": "",
            },
            {
                "instance_id": "b",
                "class_id": "tiny_tight",
                "size": "tiny",
                "distribution": "uniform",
                "capacity_level": "tight",
                "seed": 2,
                "method": "greedy",
                "status": "success",
                "feasible": True,
                "objective_value": 8.0,
                "runtime_seconds": 0.1,
                "error": "",
            },
            {
                "instance_id": "b",
                "class_id": "tiny_tight",
                "size": "tiny",
                "distribution": "uniform",
                "capacity_level": "tight",
                "seed": 2,
                "method": "local_search",
                "status": "success",
                "feasible": True,
                "objective_value": 8.0,
                "runtime_seconds": 0.25,
                "error": "",
            },
        ]
    )


def test_pairwise_classifies_repair_and_equal() -> None:
    comparison = build_pairwise_comparison(sample_results())

    classifications = dict(
        zip(comparison["instance_id"], comparison["comparison"])
    )

    assert classifications == {
        "a": "repaired",
        "b": "equal",
    }


def test_pairwise_summary_is_paired() -> None:
    comparison = build_pairwise_comparison(sample_results())
    summary = summarize_pairwise(comparison)

    assert summary["instances"] == 2
    assert summary["repaired"] == 1
    assert summary["equal"] == 1
    assert summary["improved"] == 0
    assert summary["average_objective_delta_on_shared"] == pytest.approx(0.0)


def test_aggregate_by_class_counts_runs_and_errors() -> None:
    summary = aggregate_by_class(sample_results())

    greedy = summary[summary["method"] == "greedy"].iloc[0]
    local_search = summary[summary["method"] == "local_search"].iloc[0]

    assert greedy["runs"] == 2
    assert greedy["feasible_runs"] == 1
    assert greedy["errors"] == 1
    assert local_search["feasible_runs"] == 2
