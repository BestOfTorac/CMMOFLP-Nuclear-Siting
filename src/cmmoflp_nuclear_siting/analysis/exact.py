"""Analisi comparativa dei metodi esatti sul pilot."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = {
    "instance_id",
    "class_id",
    "size",
    "distribution",
    "capacity_level",
    "seed",
    "method",
    "status",
    "feasible",
    "objective_value",
    "runtime_seconds",
    "solver_time_seconds",
    "open_sites",
}


def load_exact_results(path: Path) -> pd.DataFrame:
    """Carica e valida il CSV dei metodi esatti."""

    dataframe = pd.read_csv(path)
    missing = sorted(REQUIRED_COLUMNS - set(dataframe.columns))

    if missing:
        raise ValueError(
            "Colonne mancanti nel CSV esatto: " + ", ".join(missing)
        )

    dataframe = dataframe.copy()

    if dataframe["feasible"].dtype != bool:
        dataframe["feasible"] = (
            dataframe["feasible"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map({"true": True, "false": False})
            .fillna(False)
        )

    return dataframe


def build_exact_comparison(
    dataframe: pd.DataFrame,
    tolerance: float = 1e-8,
) -> pd.DataFrame:
    """Confronta compact e threshold istanza per istanza."""

    required_methods = {"compact", "threshold"}
    available_methods = set(dataframe["method"].unique())
    missing_methods = sorted(required_methods - available_methods)

    if missing_methods:
        raise ValueError(
            "Metodi esatti mancanti: " + ", ".join(missing_methods)
        )

    metadata_columns = [
        "instance_id",
        "class_id",
        "size",
        "distribution",
        "capacity_level",
        "seed",
    ]

    metadata = (
        dataframe[metadata_columns]
        .drop_duplicates(subset=["instance_id"])
        .set_index("instance_id")
    )

    pivot = dataframe[
        dataframe["method"].isin(required_methods)
    ].pivot(
        index="instance_id",
        columns="method",
        values=[
            "status",
            "feasible",
            "objective_value",
            "runtime_seconds",
            "solver_time_seconds",
            "open_sites",
        ],
    )

    pivot.columns = [
        f"{method}_{metric}"
        for metric, method in pivot.columns
    ]

    comparison = metadata.join(pivot).reset_index()

    comparison["objective_delta"] = (
        comparison["threshold_objective_value"]
        - comparison["compact_objective_value"]
    )
    comparison["same_objective"] = (
        comparison["objective_delta"].abs() <= tolerance
    )

    comparison["same_open_sites"] = (
        comparison["threshold_open_sites"].fillna("").astype(str)
        == comparison["compact_open_sites"].fillna("").astype(str)
    )

    comparison["runtime_ratio_threshold_over_compact"] = (
        comparison["threshold_runtime_seconds"]
        / comparison["compact_runtime_seconds"]
    )
    comparison["solver_ratio_threshold_over_compact"] = (
        comparison["threshold_solver_time_seconds"]
        / comparison["compact_solver_time_seconds"]
    )

    comparison["both_solved"] = (
        (comparison["compact_status"] == "solved")
        & (comparison["threshold_status"] == "solved")
        & comparison["compact_feasible"].astype(bool)
        & comparison["threshold_feasible"].astype(bool)
    )

    return comparison


def summarize_exact_comparison(
    dataframe: pd.DataFrame,
    comparison: pd.DataFrame,
) -> dict[str, Any]:
    """Calcola le statistiche principali dei due metodi esatti."""

    by_method = (
        dataframe.groupby("method", dropna=False)
        .agg(
            runs=("instance_id", "count"),
            solved=("feasible", "sum"),
            average_runtime_seconds=("runtime_seconds", "mean"),
            median_runtime_seconds=("runtime_seconds", "median"),
            average_solver_time_seconds=("solver_time_seconds", "mean"),
            median_solver_time_seconds=("solver_time_seconds", "median"),
        )
        .to_dict(orient="index")
    )

    return {
        "instances": int(comparison["instance_id"].nunique()),
        "both_solved": int(comparison["both_solved"].sum()),
        "same_objective": int(comparison["same_objective"].sum()),
        "same_open_sites": int(comparison["same_open_sites"].sum()),
        "max_absolute_objective_delta": float(
            comparison["objective_delta"].abs().max()
        ),
        "average_runtime_ratio": float(
            comparison["runtime_ratio_threshold_over_compact"].mean()
        ),
        "median_runtime_ratio": float(
            comparison["runtime_ratio_threshold_over_compact"].median()
        ),
        "average_solver_ratio": float(
            comparison["solver_ratio_threshold_over_compact"].mean()
        ),
        "median_solver_ratio": float(
            comparison["solver_ratio_threshold_over_compact"].median()
        ),
        "by_method": by_method,
    }


def aggregate_exact_by_class(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Aggrega tempi e risultati per classe e metodo."""

    return (
        dataframe.groupby(
            [
                "class_id",
                "size",
                "distribution",
                "capacity_level",
                "method",
            ],
            dropna=False,
        )
        .agg(
            runs=("instance_id", "count"),
            solved=("feasible", "sum"),
            average_objective=("objective_value", "mean"),
            average_runtime_seconds=("runtime_seconds", "mean"),
            median_runtime_seconds=("runtime_seconds", "median"),
            average_solver_time_seconds=("solver_time_seconds", "mean"),
        )
        .reset_index()
    )


def save_exact_analysis(
    raw_results_path: Path,
    pairwise_output_path: Path,
    class_output_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Esegue l'analisi e salva i CSV aggregati."""

    dataframe = load_exact_results(raw_results_path)
    comparison = build_exact_comparison(dataframe)
    class_summary = aggregate_exact_by_class(dataframe)
    summary = summarize_exact_comparison(dataframe, comparison)

    pairwise_output_path.parent.mkdir(parents=True, exist_ok=True)
    class_output_path.parent.mkdir(parents=True, exist_ok=True)

    comparison.to_csv(pairwise_output_path, index=False)
    class_summary.to_csv(class_output_path, index=False)

    return comparison, class_summary, summary
