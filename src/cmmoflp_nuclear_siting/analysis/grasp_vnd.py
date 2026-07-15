"""Analisi multi-seed di GRASP-VND rispetto al modello compatto."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


GRASP_REQUIRED_COLUMNS = {
    "instance_id",
    "class_id",
    "size",
    "distribution",
    "capacity_level",
    "instance_seed",
    "algorithm_seed",
    "method",
    "status",
    "feasible",
    "objective_value",
    "runtime_seconds",
    "time_to_best_seconds",
    "starts_completed",
    "repair_attempts",
    "repair_successes",
    "one_swap_moves",
    "two_swap_moves",
    "objective_upper_bound",
    "optimality_certified_by_upper_bound",
}

EXACT_REQUIRED_COLUMNS = {
    "instance_id",
    "method",
    "feasible",
    "objective_value",
}


def _normalize_boolean(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series

    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False})
        .fillna(False)
        .astype(bool)
    )


def load_grasp_vnd_analysis_inputs(
    grasp_results_path: Path,
    exact_results_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carica e valida risultati GRASP-VND ed esatti."""

    grasp = pd.read_csv(grasp_results_path)
    exact = pd.read_csv(exact_results_path)

    missing_grasp = sorted(
        GRASP_REQUIRED_COLUMNS - set(grasp.columns)
    )
    missing_exact = sorted(
        EXACT_REQUIRED_COLUMNS - set(exact.columns)
    )

    if missing_grasp:
        raise ValueError(
            "Colonne mancanti nei risultati GRASP-VND: "
            + ", ".join(missing_grasp)
        )
    if missing_exact:
        raise ValueError(
            "Colonne mancanti nei risultati esatti: "
            + ", ".join(missing_exact)
        )

    grasp = grasp.copy()
    exact = exact.copy()

    grasp["feasible"] = _normalize_boolean(grasp["feasible"])
    grasp["optimality_certified_by_upper_bound"] = (
        _normalize_boolean(
            grasp["optimality_certified_by_upper_bound"]
        )
    )
    exact["feasible"] = _normalize_boolean(exact["feasible"])

    return grasp, exact


def build_grasp_vnd_seed_comparison(
    grasp: pd.DataFrame,
    exact: pd.DataFrame,
    exact_method: str = "compact",
    tolerance: float = 1e-8,
) -> pd.DataFrame:
    """Aggiunge ottimo, gap e indicatori a ogni esecuzione."""

    reference = exact[
        (exact["method"] == exact_method)
        & exact["feasible"]
        & exact["objective_value"].notna()
    ][["instance_id", "objective_value"]].copy()

    if reference.empty:
        raise ValueError(
            f"Nessun riferimento esatto per {exact_method!r}."
        )

    duplicated = reference["instance_id"].duplicated(keep=False)
    if duplicated.any():
        raise ValueError(
            "Il riferimento esatto contiene istanze duplicate."
        )

    reference = reference.rename(
        columns={"objective_value": "optimal_objective"}
    )

    comparison = grasp.merge(
        reference,
        on="instance_id",
        how="left",
        validate="many_to_one",
    )

    comparison["comparable"] = (
        comparison["feasible"]
        & comparison["objective_value"].notna()
        & comparison["optimal_objective"].notna()
        & (comparison["optimal_objective"].abs() > tolerance)
    )

    comparison["gap_percent"] = pd.NA
    comparison.loc[
        comparison["comparable"],
        "gap_percent",
    ] = (
        (
            comparison.loc[
                comparison["comparable"],
                "optimal_objective",
            ]
            - comparison.loc[
                comparison["comparable"],
                "objective_value",
            ]
        )
        / comparison.loc[
            comparison["comparable"],
            "optimal_objective",
        ]
        * 100.0
    )
    comparison["gap_percent"] = pd.to_numeric(
        comparison["gap_percent"],
        errors="coerce",
    )

    near_zero = (
        comparison["gap_percent"].notna()
        & (comparison["gap_percent"].abs() <= tolerance * 100.0)
    )
    comparison.loc[near_zero, "gap_percent"] = 0.0

    comparison["optimal_match"] = (
        comparison["comparable"]
        & (
            (
                comparison["objective_value"]
                - comparison["optimal_objective"]
            ).abs()
            <= tolerance
        )
    )

    comparison["upper_bound_tight"] = (
        comparison["objective_upper_bound"].notna()
        & comparison["optimal_objective"].notna()
        & (
            (
                comparison["objective_upper_bound"]
                - comparison["optimal_objective"]
            ).abs()
            <= tolerance
        )
    )

    comparison["seed_success"] = (
        comparison["feasible"]
        & comparison["optimal_match"]
    )

    return comparison


def aggregate_grasp_vnd_by_instance(
    comparison: pd.DataFrame,
) -> pd.DataFrame:
    """Aggrega stabilità e prestazioni sui seed di ogni istanza."""

    def population_std(series: pd.Series) -> float:
        return float(series.std(ddof=0)) if len(series) else float("nan")

    return (
        comparison.groupby(
            [
                "instance_id",
                "class_id",
                "size",
                "distribution",
                "capacity_level",
            ],
            dropna=False,
        )
        .agg(
            algorithm_seeds=("algorithm_seed", "count"),
            feasible_runs=("feasible", "sum"),
            optimal_runs=("optimal_match", "sum"),
            certified_runs=(
                "optimality_certified_by_upper_bound",
                "sum",
            ),
            best_objective=("objective_value", "max"),
            average_objective=("objective_value", "mean"),
            objective_std=("objective_value", population_std),
            worst_objective=("objective_value", "min"),
            best_gap_percent=("gap_percent", "min"),
            average_gap_percent=("gap_percent", "mean"),
            gap_std=("gap_percent", population_std),
            worst_gap_percent=("gap_percent", "max"),
            average_runtime_seconds=("runtime_seconds", "mean"),
            median_runtime_seconds=("runtime_seconds", "median"),
            average_time_to_best_seconds=(
                "time_to_best_seconds",
                "mean",
            ),
            average_starts_completed=("starts_completed", "mean"),
            total_repair_attempts=("repair_attempts", "sum"),
            total_repair_successes=("repair_successes", "sum"),
            total_one_swap_moves=("one_swap_moves", "sum"),
            total_two_swap_moves=("two_swap_moves", "sum"),
            upper_bound_tight=("upper_bound_tight", "all"),
        )
        .reset_index()
    )


def aggregate_grasp_vnd_by_class(
    per_instance: pd.DataFrame,
) -> pd.DataFrame:
    """Aggrega i risultati per classe di istanze."""

    return (
        per_instance.groupby(
            [
                "class_id",
                "size",
                "distribution",
                "capacity_level",
            ],
            dropna=False,
        )
        .agg(
            instances=("instance_id", "count"),
            total_seed_runs=("algorithm_seeds", "sum"),
            feasible_runs=("feasible_runs", "sum"),
            optimal_runs=("optimal_runs", "sum"),
            certified_runs=("certified_runs", "sum"),
            average_best_gap_percent=(
                "best_gap_percent",
                "mean",
            ),
            average_gap_percent=("average_gap_percent", "mean"),
            maximum_worst_gap_percent=(
                "worst_gap_percent",
                "max",
            ),
            average_objective_std=("objective_std", "mean"),
            average_runtime_seconds=(
                "average_runtime_seconds",
                "mean",
            ),
            average_starts_completed=(
                "average_starts_completed",
                "mean",
            ),
        )
        .reset_index()
    )


def summarize_grasp_vnd_multi_seed(
    comparison: pd.DataFrame,
    per_instance: pd.DataFrame,
) -> dict[str, Any]:
    """Calcola il riepilogo globale della campagna multi-seed."""

    gaps = comparison.loc[
        comparison["comparable"],
        "gap_percent",
    ].dropna()

    return {
        "instances": int(per_instance["instance_id"].nunique()),
        "seed_runs": int(len(comparison)),
        "feasible_runs": int(comparison["feasible"].sum()),
        "optimal_runs": int(comparison["optimal_match"].sum()),
        "certified_runs": int(
            comparison[
                "optimality_certified_by_upper_bound"
            ].sum()
        ),
        "instances_optimal_for_all_seeds": int(
            (
                per_instance["optimal_runs"]
                == per_instance["algorithm_seeds"]
            ).sum()
        ),
        "instances_feasible_for_all_seeds": int(
            (
                per_instance["feasible_runs"]
                == per_instance["algorithm_seeds"]
            ).sum()
        ),
        "average_gap_percent": (
            float(gaps.mean()) if not gaps.empty else None
        ),
        "maximum_gap_percent": (
            float(gaps.max()) if not gaps.empty else None
        ),
        "average_runtime_seconds": float(
            comparison["runtime_seconds"].mean()
        ),
        "median_runtime_seconds": float(
            comparison["runtime_seconds"].median()
        ),
        "average_time_to_best_seconds": float(
            comparison["time_to_best_seconds"].mean()
        ),
        "average_starts_completed": float(
            comparison["starts_completed"].mean()
        ),
    }


def save_grasp_vnd_multi_seed_analysis(
    grasp_results_path: Path,
    exact_results_path: Path,
    seed_output_path: Path,
    instance_output_path: Path,
    class_output_path: Path,
    exact_method: str = "compact",
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    dict[str, Any],
]:
    """Esegue l'analisi completa e salva i CSV."""

    grasp, exact = load_grasp_vnd_analysis_inputs(
        grasp_results_path,
        exact_results_path,
    )
    comparison = build_grasp_vnd_seed_comparison(
        grasp,
        exact,
        exact_method=exact_method,
    )
    per_instance = aggregate_grasp_vnd_by_instance(comparison)
    per_class = aggregate_grasp_vnd_by_class(per_instance)
    summary = summarize_grasp_vnd_multi_seed(
        comparison,
        per_instance,
    )

    seed_output_path.parent.mkdir(parents=True, exist_ok=True)
    instance_output_path.parent.mkdir(parents=True, exist_ok=True)
    class_output_path.parent.mkdir(parents=True, exist_ok=True)

    comparison.to_csv(seed_output_path, index=False)
    per_instance.to_csv(instance_output_path, index=False)
    per_class.to_csv(class_output_path, index=False)

    return comparison, per_instance, per_class, summary
