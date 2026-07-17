"""Aggrega i risultati definitivi del benchmark CMMOFLP.

Il programma non modifica i risultati grezzi. Produce tabelle CSV
riproducibili nella cartella results/processed.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


TOLERANCE = 1e-7


def gap_percent(reference: pd.Series, value: pd.Series) -> pd.Series:
    """Calcola il gap percentuale per un problema di massimizzazione."""

    gap = 100.0 * (reference - value) / reference.abs()
    return gap.mask(gap.abs() <= TOLERANCE, 0.0)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggrega i risultati del benchmark finale."
    )
    parser.add_argument(
        "--heuristics",
        type=Path,
        default=Path("results/final/raw/final_heuristics.csv"),
    )
    parser.add_argument(
        "--grasp-vnd",
        type=Path,
        default=Path("results/final/raw/final_grasp_vnd.csv"),
    )
    parser.add_argument(
        "--exact",
        type=Path,
        default=Path("results/final/raw/final_exact.csv"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/final/summary"),
    )
    return parser.parse_args()


def validate_inputs(
    heuristics: pd.DataFrame,
    grasp_vnd: pd.DataFrame,
    exact: pd.DataFrame,
) -> None:
    required_heuristics = {
        "instance_id",
        "method",
        "size",
        "distribution",
        "capacity_level",
        "feasible",
        "objective_value",
        "runtime_seconds",
    }
    required_grasp = {
        "instance_id",
        "algorithm_seed",
        "size",
        "distribution",
        "capacity_level",
        "status",
        "feasible",
        "objective_value",
        "runtime_seconds",
        "time_to_best_seconds",
        "optimality_certified_by_upper_bound",
        "stop_reason",
    }
    required_exact = {
        "instance_id",
        "size",
        "distribution",
        "capacity_level",
        "has_incumbent",
        "optimality_certified",
        "objective_value",
        "best_bound",
        "relative_mip_gap",
        "runtime_seconds",
        "solver_time_seconds",
        "termination_reason",
    }

    for name, frame, required in (
        ("heuristics", heuristics, required_heuristics),
        ("grasp_vnd", grasp_vnd, required_grasp),
        ("exact", exact, required_exact),
    ):
        missing = sorted(required - set(frame.columns))
        if missing:
            raise ValueError(
                f"Colonne mancanti in {name}: {', '.join(missing)}"
            )

    if exact["instance_id"].duplicated().any():
        raise ValueError("Il file exact contiene istanze duplicate.")

    if grasp_vnd[
        ["instance_id", "algorithm_seed"]
    ].duplicated().any():
        raise ValueError(
            "Il file GRASP-VND contiene coppie istanza-seed duplicate."
        )

    if heuristics[
        ["instance_id", "method"]
    ].duplicated().any():
        raise ValueError(
            "Il file delle baseline contiene coppie istanza-metodo duplicate."
        )


def build_exact_summary(exact: pd.DataFrame) -> pd.DataFrame:
    return (
        exact.groupby("size", as_index=False)
        .agg(
            instances=("instance_id", "size"),
            incumbents=("has_incumbent", "sum"),
            certified_optima=("optimality_certified", "sum"),
            runtime_mean_seconds=("runtime_seconds", "mean"),
            runtime_max_seconds=("runtime_seconds", "max"),
            solver_mean_seconds=("solver_time_seconds", "mean"),
            solver_max_seconds=("solver_time_seconds", "max"),
        )
        .sort_values("size")
    )


def build_baseline_summary(
    heuristics: pd.DataFrame,
    certified_exact: pd.DataFrame,
) -> pd.DataFrame:
    merged = heuristics.merge(
        certified_exact[["instance_id", "objective_value"]],
        on="instance_id",
        how="left",
        suffixes=("", "_optimum"),
    )
    merged["gap_percent"] = gap_percent(
        merged["objective_value_optimum"],
        merged["objective_value"],
    )
    merged["known_optimum"] = merged[
        "objective_value_optimum"
    ].notna()
    merged["optimal"] = (
        merged["known_optimum"]
        & merged["feasible"]
        & (merged["gap_percent"].abs() <= TOLERANCE)
    )

    summary = (
        merged.groupby(["method", "size"], as_index=False)
        .agg(
            instances=("instance_id", "size"),
            feasible_instances=("feasible", "sum"),
            known_optimum_instances=("known_optimum", "sum"),
            optimal_instances=("optimal", "sum"),
            gap_mean_percent=("gap_percent", "mean"),
            gap_median_percent=("gap_percent", "median"),
            gap_max_percent=("gap_percent", "max"),
            runtime_mean_seconds=("runtime_seconds", "mean"),
            runtime_max_seconds=("runtime_seconds", "max"),
        )
        .sort_values(["method", "size"])
    )
    return summary


def build_h2_run_summary(
    grasp_vnd: pd.DataFrame,
    certified_exact: pd.DataFrame,
) -> pd.DataFrame:
    merged = grasp_vnd.merge(
        certified_exact[["instance_id", "objective_value"]],
        on="instance_id",
        how="left",
        suffixes=("", "_optimum"),
    )
    merged["gap_percent"] = gap_percent(
        merged["objective_value_optimum"],
        merged["objective_value"],
    )
    merged["known_optimum"] = merged[
        "objective_value_optimum"
    ].notna()
    merged["optimal"] = (
        merged["known_optimum"]
        & merged["feasible"]
        & (merged["gap_percent"].abs() <= TOLERANCE)
    )

    return (
        merged.groupby("size", as_index=False)
        .agg(
            runs=("instance_id", "size"),
            feasible_runs=("feasible", "sum"),
            known_optimum_runs=("known_optimum", "sum"),
            optimal_runs=("optimal", "sum"),
            upper_bound_certified_runs=(
                "optimality_certified_by_upper_bound",
                "sum",
            ),
            gap_mean_percent=("gap_percent", "mean"),
            gap_median_percent=("gap_percent", "median"),
            gap_max_percent=("gap_percent", "max"),
            runtime_mean_seconds=("runtime_seconds", "mean"),
            runtime_max_seconds=("runtime_seconds", "max"),
            time_to_best_mean_seconds=(
                "time_to_best_seconds",
                "mean",
            ),
        )
        .sort_values("size")
    )


def build_h2_instance_summary(
    grasp_vnd: pd.DataFrame,
    exact: pd.DataFrame,
) -> pd.DataFrame:
    grouped = (
        grasp_vnd.groupby(
            [
                "instance_id",
                "size",
                "distribution",
                "capacity_level",
            ],
            as_index=False,
        )
        .agg(
            runs=("algorithm_seed", "size"),
            feasible_runs=("feasible", "sum"),
            upper_bound_certified_runs=(
                "optimality_certified_by_upper_bound",
                "sum",
            ),
            h2_best=("objective_value", "max"),
            h2_average=("objective_value", "mean"),
            h2_worst=("objective_value", "min"),
            h2_runtime_mean_seconds=("runtime_seconds", "mean"),
            h2_runtime_sum_seconds=("runtime_seconds", "sum"),
            h2_time_to_best_mean_seconds=(
                "time_to_best_seconds",
                "mean",
            ),
        )
    )

    exact_columns = [
        "instance_id",
        "has_incumbent",
        "optimality_certified",
        "objective_value",
        "best_bound",
        "relative_mip_gap",
        "runtime_seconds",
        "solver_time_seconds",
        "termination_reason",
    ]
    merged = grouped.merge(
        exact[exact_columns],
        on="instance_id",
        how="left",
    ).rename(
        columns={
            "objective_value": "compact_incumbent",
            "runtime_seconds": "compact_runtime_seconds",
            "solver_time_seconds": "compact_solver_seconds",
        }
    )

    known = merged["optimality_certified"].fillna(False)
    merged["known_optimum"] = known
    merged["best_gap_percent"] = float("nan")
    merged["average_gap_percent"] = float("nan")
    merged["worst_gap_percent"] = float("nan")

    merged.loc[known, "best_gap_percent"] = gap_percent(
        merged.loc[known, "compact_incumbent"],
        merged.loc[known, "h2_best"],
    )
    merged.loc[known, "average_gap_percent"] = gap_percent(
        merged.loc[known, "compact_incumbent"],
        merged.loc[known, "h2_average"],
    )
    merged.loc[known, "worst_gap_percent"] = gap_percent(
        merged.loc[known, "compact_incumbent"],
        merged.loc[known, "h2_worst"],
    )

    merged["h2_vs_compact_incumbent_percent"] = (
        100.0
        * (merged["h2_best"] - merged["compact_incumbent"])
        / merged["compact_incumbent"].abs()
    )
    merged["compact_bound_gap_from_h2_percent"] = (
        100.0
        * (merged["best_bound"] - merged["h2_best"])
        / merged["h2_best"].abs()
    )

    return merged.sort_values(
        ["size", "distribution", "capacity_level", "instance_id"]
    )


def build_h2_best_summary(
    h2_instances: pd.DataFrame,
) -> pd.DataFrame:
    frame = h2_instances.copy()
    frame["optimal_best"] = (
        frame["known_optimum"].fillna(False)
        & (
            pd.to_numeric(
                frame["best_gap_percent"],
                errors="coerce",
            ).abs()
            <= TOLERANCE
        )
    )

    return (
        frame.groupby("size", as_index=False)
        .agg(
            instances=("instance_id", "size"),
            instances_with_feasible_h2=(
                "feasible_runs",
                lambda values: (values > 0).sum(),
            ),
            known_optimum_instances=("known_optimum", "sum"),
            optimal_best_of_five=("optimal_best", "sum"),
            best_gap_mean_percent=("best_gap_percent", "mean"),
            best_gap_median_percent=("best_gap_percent", "median"),
            best_gap_max_percent=("best_gap_percent", "max"),
            average_gap_mean_percent=(
                "average_gap_percent",
                "mean",
            ),
            worst_gap_max_percent=("worst_gap_percent", "max"),
            h2_runtime_mean_per_run_seconds=(
                "h2_runtime_mean_seconds",
                "mean",
            ),
            h2_runtime_mean_five_runs_seconds=(
                "h2_runtime_sum_seconds",
                "mean",
            ),
        )
        .sort_values("size")
    )


def build_class_summary(
    grasp_vnd: pd.DataFrame,
    exact: pd.DataFrame,
) -> pd.DataFrame:
    h2 = (
        grasp_vnd.groupby(
            ["size", "distribution", "capacity_level"],
            as_index=False,
        )
        .agg(
            h2_runs=("instance_id", "size"),
            h2_feasible_runs=("feasible", "sum"),
            h2_upper_bound_certified_runs=(
                "optimality_certified_by_upper_bound",
                "sum",
            ),
            h2_runtime_mean_seconds=("runtime_seconds", "mean"),
            h2_time_to_best_mean_seconds=(
                "time_to_best_seconds",
                "mean",
            ),
        )
    )
    compact = (
        exact.groupby(
            ["size", "distribution", "capacity_level"],
            as_index=False,
        )
        .agg(
            compact_instances=("instance_id", "size"),
            compact_incumbents=("has_incumbent", "sum"),
            compact_certified_optima=(
                "optimality_certified",
                "sum",
            ),
            compact_runtime_mean_seconds=(
                "runtime_seconds",
                "mean",
            ),
            compact_solver_mean_seconds=(
                "solver_time_seconds",
                "mean",
            ),
        )
    )
    return h2.merge(
        compact,
        on=["size", "distribution", "capacity_level"],
        how="outer",
    ).sort_values(["size", "distribution", "capacity_level"])


def main() -> int:
    args = parse_arguments()

    heuristics = pd.read_csv(args.heuristics)
    grasp_vnd = pd.read_csv(args.grasp_vnd)
    exact = pd.read_csv(args.exact)

    validate_inputs(heuristics, grasp_vnd, exact)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    certified_exact = exact[
        exact["optimality_certified"].fillna(False)
    ].copy()

    exact_summary = build_exact_summary(exact)
    baseline_summary = build_baseline_summary(
        heuristics,
        certified_exact,
    )
    h2_run_summary = build_h2_run_summary(
        grasp_vnd,
        certified_exact,
    )
    h2_instances = build_h2_instance_summary(
        grasp_vnd,
        exact,
    )
    h2_best_summary = build_h2_best_summary(h2_instances)
    class_summary = build_class_summary(grasp_vnd, exact)
    noncertified = h2_instances[
        ~h2_instances["known_optimum"].fillna(False)
    ].copy()

    outputs = {
        "exact_summary.csv": exact_summary,
        "baseline_summary.csv": baseline_summary,
        "h2_run_summary.csv": h2_run_summary,
        "h2_best_of_five_summary.csv": h2_best_summary,
        "h2_instance_summary.csv": h2_instances,
        "class_summary.csv": class_summary,
        "noncertified_instances.csv": noncertified,
    }

    for filename, frame in outputs.items():
        frame.to_csv(args.output_dir / filename, index=False)

    total_h2_runs = len(grasp_vnd)
    total_h2_feasible = int(grasp_vnd["feasible"].sum())
    total_exact_certified = int(exact["optimality_certified"].sum())
    known_instances = int(h2_instances["known_optimum"].sum())

    optimal_best = (
        pd.to_numeric(
            h2_instances["best_gap_percent"],
            errors="coerce",
        ).abs()
        <= TOLERANCE
    ).sum()

    print("\n=== ANALISI FINALE DEL BENCHMARK ===")
    print(f"Istanze: {exact['instance_id'].nunique()}")
    print(
        "Ottimi compact certificati: "
        f"{total_exact_certified}/{len(exact)}"
    )
    print(
        "Run H2 ammissibili: "
        f"{total_h2_feasible}/{total_h2_runs}"
    )
    print(
        "Istanze H2 best-of-5 ottime: "
        f"{int(optimal_best)}/{known_instances} "
        "(solo ottimi noti)"
    )
    print(
        "Istanze senza ottimo certificato: "
        f"{len(noncertified)}"
    )
    print(f"Output: {args.output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
