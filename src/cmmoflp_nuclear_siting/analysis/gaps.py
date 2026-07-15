"""Calcolo dei gap delle euristiche rispetto alla soluzione esatta."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


HEURISTIC_REQUIRED_COLUMNS = {
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
    "open_sites",
}

EXACT_REQUIRED_COLUMNS = {
    "instance_id",
    "method",
    "status",
    "feasible",
    "objective_value",
    "runtime_seconds",
    "open_sites",
}


def _normalize_boolean(series: pd.Series) -> pd.Series:
    """Converte una colonna booleana letta da CSV."""

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


def load_gap_inputs(
    heuristic_results_path: Path,
    exact_results_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carica e valida i risultati euristici ed esatti."""

    heuristics = pd.read_csv(heuristic_results_path)
    exact = pd.read_csv(exact_results_path)

    missing_heuristic = sorted(
        HEURISTIC_REQUIRED_COLUMNS - set(heuristics.columns)
    )
    missing_exact = sorted(EXACT_REQUIRED_COLUMNS - set(exact.columns))

    if missing_heuristic:
        raise ValueError(
            "Colonne mancanti nei risultati euristici: "
            + ", ".join(missing_heuristic)
        )
    if missing_exact:
        raise ValueError(
            "Colonne mancanti nei risultati esatti: "
            + ", ".join(missing_exact)
        )

    heuristics = heuristics.copy()
    exact = exact.copy()

    heuristics["feasible"] = _normalize_boolean(heuristics["feasible"])
    exact["feasible"] = _normalize_boolean(exact["feasible"])

    return heuristics, exact


def build_heuristic_gap_table(
    heuristics: pd.DataFrame,
    exact: pd.DataFrame,
    exact_method: str = "compact",
    tolerance: float = 1e-8,
) -> pd.DataFrame:
    """Confronta ogni soluzione euristica con il riferimento esatto.

    Per un problema di massimizzazione:

        gap = (z* - z_H) / z* * 100

    dove ``z*`` è il valore esatto e ``z_H`` quello euristico.
    """

    if tolerance < 0:
        raise ValueError("La tolleranza non può essere negativa.")

    reference = exact[
        (exact["method"] == exact_method)
        & exact["feasible"]
        & exact["objective_value"].notna()
    ].copy()

    if reference.empty:
        raise ValueError(
            f"Nessun risultato esatto disponibile per il metodo {exact_method!r}."
        )

    duplicated = reference["instance_id"].duplicated(keep=False)
    if duplicated.any():
        duplicates = sorted(
            reference.loc[duplicated, "instance_id"].astype(str).unique()
        )
        raise ValueError(
            "Risultati esatti duplicati per le istanze: "
            + ", ".join(duplicates)
        )

    reference = reference[
        [
            "instance_id",
            "objective_value",
            "runtime_seconds",
            "open_sites",
        ]
    ].rename(
        columns={
            "objective_value": "optimal_objective",
            "runtime_seconds": "exact_runtime_seconds",
            "open_sites": "optimal_open_sites",
        }
    )

    selected = heuristics.copy().rename(
        columns={
            "status": "heuristic_status",
            "feasible": "heuristic_feasible",
            "objective_value": "heuristic_objective",
            "runtime_seconds": "heuristic_runtime_seconds",
            "open_sites": "heuristic_open_sites",
        }
    )

    comparison = selected.merge(
        reference,
        how="left",
        on="instance_id",
        validate="many_to_one",
    )

    comparison["exact_available"] = (
        comparison["optimal_objective"].notna()
    )
    comparison["comparable"] = (
        comparison["exact_available"]
        & comparison["heuristic_feasible"].fillna(False).astype(bool)
        & (comparison["heuristic_status"] == "success")
        & comparison["heuristic_objective"].notna()
        & (comparison["optimal_objective"].abs() > tolerance)
    )

    comparison["objective_difference"] = pd.NA
    comparison.loc[
        comparison["comparable"],
        "objective_difference",
    ] = (
        comparison.loc[
            comparison["comparable"],
            "optimal_objective",
        ]
        - comparison.loc[
            comparison["comparable"],
            "heuristic_objective",
        ]
    )
    comparison["objective_difference"] = pd.to_numeric(
        comparison["objective_difference"],
        errors="coerce",
    )

    comparison["gap_percent"] = pd.NA
    comparison.loc[
        comparison["comparable"],
        "gap_percent",
    ] = (
        comparison.loc[
            comparison["comparable"],
            "objective_difference",
        ]
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
    comparison.loc[near_zero, "objective_difference"] = 0.0

    comparison["optimal_match"] = (
        comparison["comparable"]
        & (
            comparison["objective_difference"].abs()
            <= tolerance
        )
    )

    comparison["speedup_exact_over_heuristic"] = pd.NA
    valid_runtime = (
        comparison["comparable"]
        & (comparison["heuristic_runtime_seconds"] > 0)
    )
    comparison.loc[
        valid_runtime,
        "speedup_exact_over_heuristic",
    ] = (
        comparison.loc[valid_runtime, "exact_runtime_seconds"]
        / comparison.loc[valid_runtime, "heuristic_runtime_seconds"]
    )
    comparison["speedup_exact_over_heuristic"] = pd.to_numeric(
        comparison["speedup_exact_over_heuristic"],
        errors="coerce",
    )

    comparison["quality_status"] = "not_comparable"
    comparison.loc[
        ~comparison["exact_available"],
        "quality_status",
    ] = "exact_missing"
    comparison.loc[
        comparison["exact_available"]
        & ~comparison["heuristic_feasible"].fillna(False).astype(bool),
        "quality_status",
    ] = "heuristic_failed"
    comparison.loc[
        comparison["comparable"]
        & comparison["optimal_match"],
        "quality_status",
    ] = "optimal"
    comparison.loc[
        comparison["comparable"]
        & ~comparison["optimal_match"]
        & (comparison["gap_percent"] > 0),
        "quality_status",
    ] = "suboptimal"
    comparison.loc[
        comparison["comparable"]
        & (comparison["gap_percent"] < 0),
        "quality_status",
    ] = "inconsistent_better_than_exact"

    return comparison


def summarize_heuristic_gaps(
    comparison: pd.DataFrame,
) -> dict[str, dict[str, Any]]:
    """Calcola un riepilogo complessivo per metodo euristico."""

    summary: dict[str, dict[str, Any]] = {}

    for method, group in comparison.groupby("method", dropna=False):
        comparable = group[group["comparable"]]
        gaps = comparable["gap_percent"].dropna()
        speedups = comparable[
            "speedup_exact_over_heuristic"
        ].dropna()

        summary[str(method)] = {
            "runs": int(len(group)),
            "feasible_runs": int(
                group["heuristic_feasible"].fillna(False).astype(bool).sum()
            ),
            "comparable_runs": int(len(comparable)),
            "optimal_matches": int(
                group["optimal_match"].fillna(False).astype(bool).sum()
            ),
            "suboptimal_runs": int(
                (group["quality_status"] == "suboptimal").sum()
            ),
            "failed_runs": int(
                (group["quality_status"] == "heuristic_failed").sum()
            ),
            "inconsistent_runs": int(
                (
                    group["quality_status"]
                    == "inconsistent_better_than_exact"
                ).sum()
            ),
            "average_gap_percent": (
                float(gaps.mean()) if not gaps.empty else None
            ),
            "median_gap_percent": (
                float(gaps.median()) if not gaps.empty else None
            ),
            "maximum_gap_percent": (
                float(gaps.max()) if not gaps.empty else None
            ),
            "average_speedup_vs_exact": (
                float(speedups.mean()) if not speedups.empty else None
            ),
            "median_speedup_vs_exact": (
                float(speedups.median()) if not speedups.empty else None
            ),
        }

    return summary


def aggregate_gaps_by_class(
    comparison: pd.DataFrame,
) -> pd.DataFrame:
    """Aggrega gap, robustezza e tempi per classe e metodo."""

    grouping_columns = [
        "class_id",
        "size",
        "distribution",
        "capacity_level",
        "method",
    ]

    base = (
        comparison.groupby(
            grouping_columns,
            dropna=False,
        )
        .agg(
            runs=("instance_id", "count"),
            feasible_runs=("heuristic_feasible", "sum"),
            comparable_runs=("comparable", "sum"),
            optimal_matches=("optimal_match", "sum"),
            failed_runs=(
                "quality_status",
                lambda values: int(
                    (values == "heuristic_failed").sum()
                ),
            ),
            average_heuristic_runtime_seconds=(
                "heuristic_runtime_seconds",
                "mean",
            ),
        )
        .reset_index()
    )

    comparable = comparison[comparison["comparable"]].copy()

    quality = (
        comparable.groupby(
            grouping_columns,
            dropna=False,
        )
        .agg(
            average_gap_percent=("gap_percent", "mean"),
            median_gap_percent=("gap_percent", "median"),
            maximum_gap_percent=("gap_percent", "max"),
            average_speedup_vs_exact=(
                "speedup_exact_over_heuristic",
                "mean",
            ),
        )
        .reset_index()
    )

    return base.merge(
        quality,
        how="left",
        on=grouping_columns,
    )


def save_gap_analysis(
    heuristic_results_path: Path,
    exact_results_path: Path,
    pairwise_output_path: Path,
    class_output_path: Path,
    exact_method: str = "compact",
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict[str, Any]]]:
    """Esegue l'analisi dei gap e salva i risultati aggregati."""

    heuristics, exact = load_gap_inputs(
        heuristic_results_path,
        exact_results_path,
    )
    comparison = build_heuristic_gap_table(
        heuristics,
        exact,
        exact_method=exact_method,
    )
    class_summary = aggregate_gaps_by_class(comparison)
    summary = summarize_heuristic_gaps(comparison)

    pairwise_output_path.parent.mkdir(parents=True, exist_ok=True)
    class_output_path.parent.mkdir(parents=True, exist_ok=True)

    comparison.to_csv(pairwise_output_path, index=False)
    class_summary.to_csv(class_output_path, index=False)

    return comparison, class_summary, summary
