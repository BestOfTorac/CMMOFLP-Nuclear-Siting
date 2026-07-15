"""Test dell'analisi multi-seed GRASP-VND."""

import pandas as pd
import pytest

from cmmoflp_nuclear_siting.analysis.grasp_vnd import (
    aggregate_grasp_vnd_by_instance,
    build_grasp_vnd_seed_comparison,
    summarize_grasp_vnd_multi_seed,
)


def sample_exact() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "instance_id": "a",
                "method": "compact",
                "feasible": True,
                "objective_value": 10.0,
            },
            {
                "instance_id": "b",
                "method": "compact",
                "feasible": True,
                "objective_value": 12.0,
            },
        ]
    )


def sample_grasp() -> pd.DataFrame:
    rows = []

    for instance_id, optimum, upper_bound in [
        ("a", 10.0, 10.0),
        ("b", 12.0, 13.0),
    ]:
        for algorithm_seed in [42, 123]:
            objective = optimum
            if instance_id == "b" and algorithm_seed == 123:
                objective = 11.0

            rows.append(
                {
                    "instance_id": instance_id,
                    "class_id": "tiny_uniform_tight",
                    "size": "tiny",
                    "distribution": "uniform",
                    "capacity_level": "tight",
                    "instance_seed": 1,
                    "algorithm_seed": algorithm_seed,
                    "method": "grasp_vnd",
                    "status": "success",
                    "feasible": True,
                    "objective_value": objective,
                    "runtime_seconds": 0.02,
                    "time_to_best_seconds": 0.005,
                    "starts_completed": 10,
                    "repair_attempts": 0,
                    "repair_successes": 0,
                    "one_swap_moves": 1,
                    "two_swap_moves": 1,
                    "objective_upper_bound": upper_bound,
                    "optimality_certified_by_upper_bound": (
                        instance_id == "a"
                    ),
                }
            )

    return pd.DataFrame(rows)


def test_seed_comparison_computes_gap_and_optimality() -> None:
    comparison = build_grasp_vnd_seed_comparison(
        sample_grasp(),
        sample_exact(),
    )

    suboptimal = comparison[
        (comparison["instance_id"] == "b")
        & (comparison["algorithm_seed"] == 123)
    ].iloc[0]

    assert suboptimal["gap_percent"] == pytest.approx(
        100.0 / 12.0
    )
    assert not suboptimal["optimal_match"]


def test_instance_aggregation_measures_stability() -> None:
    comparison = build_grasp_vnd_seed_comparison(
        sample_grasp(),
        sample_exact(),
    )
    per_instance = aggregate_grasp_vnd_by_instance(comparison)

    instance_a = per_instance[
        per_instance["instance_id"] == "a"
    ].iloc[0]
    instance_b = per_instance[
        per_instance["instance_id"] == "b"
    ].iloc[0]

    assert instance_a["optimal_runs"] == 2
    assert instance_a["objective_std"] == pytest.approx(0.0)
    assert instance_b["optimal_runs"] == 1
    assert instance_b["objective_std"] > 0


def test_multi_seed_summary_counts_all_runs() -> None:
    comparison = build_grasp_vnd_seed_comparison(
        sample_grasp(),
        sample_exact(),
    )
    per_instance = aggregate_grasp_vnd_by_instance(comparison)
    summary = summarize_grasp_vnd_multi_seed(
        comparison,
        per_instance,
    )

    assert summary["instances"] == 2
    assert summary["seed_runs"] == 4
    assert summary["feasible_runs"] == 4
    assert summary["optimal_runs"] == 3
    assert summary["instances_optimal_for_all_seeds"] == 1
