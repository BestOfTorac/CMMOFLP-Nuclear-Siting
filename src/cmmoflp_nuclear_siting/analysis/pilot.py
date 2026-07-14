"""Analisi comparativa dei risultati pilota."""

from __future__ import annotations

from pathlib import Path

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
}


def load_results(path: Path) -> pd.DataFrame:
    """Carica e valida il CSV dei risultati grezzi."""

    dataframe = pd.read_csv(path)
    missing = sorted(REQUIRED_COLUMNS - set(dataframe.columns))

    if missing:
        raise ValueError(
            "Colonne mancanti nel CSV: " + ", ".join(missing)
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


def build_pairwise_comparison(
    dataframe: pd.DataFrame,
    tolerance: float = 1e-9,
) -> pd.DataFrame:
    """Costruisce un confronto greedy-local search per ogni istanza."""

    methods = {"greedy", "local_search"}
    available = set(dataframe["method"].unique())
    missing_methods = sorted(methods - available)

    if missing_methods:
        raise ValueError(
            "Metodi mancanti nei risultati: " + ", ".join(missing_methods)
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

    selected = dataframe[
        dataframe["method"].isin(methods)
    ].copy()

    pivot = selected.pivot(
        index="instance_id",
        columns="method",
        values=[
            "status",
            "feasible",
            "objective_value",
            "runtime_seconds",
            "error",
        ],
    )

    pivot.columns = [
        f"{method}_{metric}"
        for metric, method in pivot.columns
    ]

    comparison = metadata.join(pivot).reset_index()

    for column in [
        "greedy_status",
        "local_search_status",
        "greedy_feasible",
        "local_search_feasible",
        "greedy_objective_value",
        "local_search_objective_value",
        "greedy_runtime_seconds",
        "local_search_runtime_seconds",
        "greedy_error",
        "local_search_error",
    ]:
        if column not in comparison:
            comparison[column] = pd.NA

    greedy_success = (
        (comparison["greedy_status"] == "success")
        & comparison["greedy_feasible"].fillna(False).astype(bool)
    )
    local_success = (
        (comparison["local_search_status"] == "success")
        & comparison["local_search_feasible"].fillna(False).astype(bool)
    )
    both_success = greedy_success & local_success

    comparison["objective_delta"] = pd.NA
    comparison.loc[both_success, "objective_delta"] = (
        comparison.loc[both_success, "local_search_objective_value"]
        - comparison.loc[both_success, "greedy_objective_value"]
    )
    comparison["objective_delta"] = pd.to_numeric(
        comparison["objective_delta"],
        errors="coerce",
    )

    comparison["comparison"] = "unclassified"
    comparison.loc[~greedy_success & local_success, "comparison"] = "repaired"
    comparison.loc[greedy_success & ~local_success, "comparison"] = "regressed"
    comparison.loc[~greedy_success & ~local_success, "comparison"] = "both_failed"

    comparison.loc[
        both_success & (comparison["objective_delta"] > tolerance),
        "comparison",
    ] = "improved"
    comparison.loc[
        both_success & (comparison["objective_delta"].abs() <= tolerance),
        "comparison",
    ] = "equal"
    comparison.loc[
        both_success & (comparison["objective_delta"] < -tolerance),
        "comparison",
    ] = "worse"

    comparison["runtime_ratio_local_over_greedy"] = pd.NA
    positive_greedy_runtime = (
        both_success
        & (comparison["greedy_runtime_seconds"] > 0)
    )
    comparison.loc[
        positive_greedy_runtime,
        "runtime_ratio_local_over_greedy",
    ] = (
        comparison.loc[
            positive_greedy_runtime,
            "local_search_runtime_seconds",
        ]
        / comparison.loc[
            positive_greedy_runtime,
            "greedy_runtime_seconds",
        ]
    )
    comparison["runtime_ratio_local_over_greedy"] = pd.to_numeric(
        comparison["runtime_ratio_local_over_greedy"],
        errors="coerce",
    )

    return comparison


def summarize_pairwise(comparison: pd.DataFrame) -> dict[str, int | float]:
    """Riassume il confronto appaiato tra le due euristiche."""

    counts = comparison["comparison"].value_counts()

    shared = comparison[
        comparison["comparison"].isin(["improved", "equal", "worse"])
    ]

    return {
        "instances": int(len(comparison)),
        "repaired": int(counts.get("repaired", 0)),
        "improved": int(counts.get("improved", 0)),
        "equal": int(counts.get("equal", 0)),
        "worse": int(counts.get("worse", 0)),
        "both_failed": int(counts.get("both_failed", 0)),
        "regressed": int(counts.get("regressed", 0)),
        "average_objective_delta_on_shared": (
            float(shared["objective_delta"].mean())
            if not shared.empty
            else 0.0
        ),
        "average_runtime_ratio_on_shared": (
            float(shared["runtime_ratio_local_over_greedy"].mean())
            if not shared.empty
            else 0.0
        ),
    }


def aggregate_by_class(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Aggrega risultati e tempi per classe e metodo."""

    successful = dataframe[
        (dataframe["status"] == "success")
        & dataframe["feasible"]
    ].copy()

    grouped = (
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
            feasible_runs=("feasible", "sum"),
            errors=("status", lambda values: int((values == "error").sum())),
            average_runtime_seconds=("runtime_seconds", "mean"),
        )
        .reset_index()
    )

    objective_means = (
        successful.groupby(
            [
                "class_id",
                "size",
                "distribution",
                "capacity_level",
                "method",
            ],
            dropna=False,
        )["objective_value"]
        .mean()
        .rename("average_objective")
        .reset_index()
    )

    return grouped.merge(
        objective_means,
        how="left",
        on=[
            "class_id",
            "size",
            "distribution",
            "capacity_level",
            "method",
        ],
    )


def save_analysis(
    raw_results_path: Path,
    pairwise_output_path: Path,
    class_output_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int | float]]:
    """Esegue l'analisi e salva i due CSV aggregati."""

    dataframe = load_results(raw_results_path)
    comparison = build_pairwise_comparison(dataframe)
    class_summary = aggregate_by_class(dataframe)
    pairwise_summary = summarize_pairwise(comparison)

    pairwise_output_path.parent.mkdir(parents=True, exist_ok=True)
    class_output_path.parent.mkdir(parents=True, exist_ok=True)

    comparison.to_csv(pairwise_output_path, index=False)
    class_summary.to_csv(class_output_path, index=False)

    return comparison, class_summary, pairwise_summary
