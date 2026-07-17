"""Analisi di ablation minima usando i risultati già prodotti.

Confronta:
- greedy;
- greedy + 1-swap;
- GRASP-VND con seed fisso 42;
- GRASP-VND best-of-5.

Non modifica né riesegue gli algoritmi.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


TOLERANCE = 1e-7
SIZE_ORDER = ["medium", "large", "xlarge"]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analizza l'ablation minima del benchmark finale."
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
        "--seed",
        type=int,
        default=42,
        help="Seed usato per rappresentare una singola run H2.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/final/ablation"),
    )
    return parser.parse_args()


def gap_percent(
    optimum: pd.Series,
    objective: pd.Series,
) -> pd.Series:
    gap = 100.0 * (optimum - objective) / optimum.abs()
    return gap.mask(gap.abs() <= TOLERANCE, 0.0)


def validate_inputs(
    heuristics: pd.DataFrame,
    grasp: pd.DataFrame,
    exact: pd.DataFrame,
    seed: int,
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
        "feasible",
        "objective_value",
        "runtime_seconds",
    }
    required_exact = {
        "instance_id",
        "optimality_certified",
        "objective_value",
    }

    for name, frame, required in (
        ("heuristics", heuristics, required_heuristics),
        ("grasp_vnd", grasp, required_grasp),
        ("exact", exact, required_exact),
    ):
        missing = sorted(required - set(frame.columns))
        if missing:
            raise ValueError(
                f"Colonne mancanti in {name}: {', '.join(missing)}"
            )

    if heuristics[
        ["instance_id", "method"]
    ].duplicated().any():
        raise ValueError(
            "Risultati baseline duplicati per istanza e metodo."
        )

    if grasp[
        ["instance_id", "algorithm_seed"]
    ].duplicated().any():
        raise ValueError(
            "Risultati H2 duplicati per istanza e seed."
        )

    if exact["instance_id"].duplicated().any():
        raise ValueError("Risultati exact duplicati per istanza.")

    if seed not in set(grasp["algorithm_seed"]):
        raise ValueError(
            f"Il seed {seed} non è presente nei risultati H2."
        )


def exact_reference(exact: pd.DataFrame) -> pd.DataFrame:
    reference = exact[
        [
            "instance_id",
            "optimality_certified",
            "objective_value",
        ]
    ].rename(columns={"objective_value": "optimum"})
    reference["known_optimum"] = reference[
        "optimality_certified"
    ].fillna(False)
    reference.loc[
        ~reference["known_optimum"],
        "optimum",
    ] = pd.NA
    return reference[
        ["instance_id", "known_optimum", "optimum"]
    ]


def build_method_rows(
    heuristics: pd.DataFrame,
    grasp: pd.DataFrame,
    exact: pd.DataFrame,
    seed: int,
) -> pd.DataFrame:
    methods: list[pd.DataFrame] = []

    labels = {
        "greedy": "Greedy",
        "local_search": "Greedy + 1-swap",
    }

    for method_name, label in labels.items():
        frame = heuristics[
            heuristics["method"] == method_name
        ].copy()
        frame["variant"] = label
        frame["runs_used"] = 1
        frame["runtime_total_seconds"] = frame[
            "runtime_seconds"
        ]
        methods.append(frame)

    single = grasp[
        grasp["algorithm_seed"] == seed
    ].copy()
    single["variant"] = f"GRASP-VND seed {seed}"
    single["runs_used"] = 1
    single["runtime_total_seconds"] = single[
        "runtime_seconds"
    ]
    methods.append(single)

    best = (
        grasp.groupby(
            [
                "instance_id",
                "size",
                "distribution",
                "capacity_level",
            ],
            as_index=False,
        )
        .agg(
            feasible=("feasible", "max"),
            objective_value=("objective_value", "max"),
            runtime_total_seconds=("runtime_seconds", "sum"),
            feasible_runs=("feasible", "sum"),
            runs_used=("algorithm_seed", "size"),
        )
    )
    best["variant"] = "GRASP-VND best-of-5"
    best["runtime_seconds"] = best[
        "runtime_total_seconds"
    ]
    methods.append(best)

    combined = pd.concat(methods, ignore_index=True, sort=False)
    combined = combined.merge(
        exact_reference(exact),
        on="instance_id",
        how="left",
    )
    combined["gap_percent"] = gap_percent(
        combined["optimum"],
        combined["objective_value"],
    )
    combined["optimal"] = (
        combined["known_optimum"]
        & combined["feasible"]
        & (combined["gap_percent"].abs() <= TOLERANCE)
    )
    return combined


def summarize_variant(
    frame: pd.DataFrame,
    scope: str,
) -> dict[str, object]:
    known = frame["known_optimum"].fillna(False)

    return {
        "scope": scope,
        "variant": frame["variant"].iloc[0],
        "instances": len(frame),
        "feasible_instances": int(frame["feasible"].sum()),
        "feasibility_rate_percent": (
            100.0 * frame["feasible"].sum() / len(frame)
        ),
        "known_optimum_instances": int(known.sum()),
        "optimal_instances": int(frame["optimal"].sum()),
        "optimal_rate_known_percent": (
            100.0 * frame["optimal"].sum() / known.sum()
            if known.sum()
            else pd.NA
        ),
        "gap_mean_percent": frame["gap_percent"].mean(),
        "gap_median_percent": frame["gap_percent"].median(),
        "gap_max_percent": frame["gap_percent"].max(),
        "runtime_mean_seconds": frame[
            "runtime_total_seconds"
        ].mean(),
        "runtime_max_seconds": frame[
            "runtime_total_seconds"
        ].max(),
    }


def build_ablation_summary(
    method_rows: pd.DataFrame,
) -> pd.DataFrame:
    records: list[dict[str, object]] = []

    for variant, frame in method_rows.groupby("variant"):
        records.append(summarize_variant(frame, "overall"))

        for size in SIZE_ORDER:
            subset = frame[frame["size"] == size]
            if not subset.empty:
                records.append(
                    summarize_variant(subset, size)
                )

    summary = pd.DataFrame(records)
    scope_order = {
        "overall": 0,
        "medium": 1,
        "large": 2,
        "xlarge": 3,
    }
    variant_order = {
        "Greedy": 0,
        "Greedy + 1-swap": 1,
        "GRASP-VND seed 42": 2,
        "GRASP-VND best-of-5": 3,
    }
    summary["_scope_order"] = summary["scope"].map(scope_order)
    summary["_variant_order"] = summary["variant"].map(
        variant_order
    )
    return (
        summary.sort_values(
            ["_scope_order", "_variant_order"]
        )
        .drop(columns=["_scope_order", "_variant_order"])
        .reset_index(drop=True)
    )


def build_local_search_effect(
    method_rows: pd.DataFrame,
) -> pd.DataFrame:
    greedy = method_rows[
        method_rows["variant"] == "Greedy"
    ][
        [
            "instance_id",
            "size",
            "feasible",
            "objective_value",
            "runtime_total_seconds",
        ]
    ].rename(
        columns={
            "feasible": "greedy_feasible",
            "objective_value": "greedy_objective",
            "runtime_total_seconds": "greedy_runtime",
        }
    )
    local = method_rows[
        method_rows["variant"] == "Greedy + 1-swap"
    ][
        [
            "instance_id",
            "feasible",
            "objective_value",
            "runtime_total_seconds",
        ]
    ].rename(
        columns={
            "feasible": "local_feasible",
            "objective_value": "local_objective",
            "runtime_total_seconds": "local_runtime",
        }
    )

    comparison = greedy.merge(local, on="instance_id")
    comparison["recovered"] = (
        ~comparison["greedy_feasible"]
        & comparison["local_feasible"]
    )
    comparison["improved"] = (
        comparison["greedy_feasible"]
        & comparison["local_feasible"]
        & (
            comparison["local_objective"]
            > comparison["greedy_objective"] + TOLERANCE
        )
    )
    comparison["worsened"] = (
        comparison["greedy_feasible"]
        & comparison["local_feasible"]
        & (
            comparison["local_objective"]
            < comparison["greedy_objective"] - TOLERANCE
        )
    )
    comparison["equal"] = (
        comparison["greedy_feasible"]
        & comparison["local_feasible"]
        & (
            (
                comparison["local_objective"]
                - comparison["greedy_objective"]
            ).abs()
            <= TOLERANCE
        )
    )
    comparison["runtime_ratio"] = (
        comparison["local_runtime"]
        / comparison["greedy_runtime"]
    )
    return comparison


def build_multiseed_effect(
    method_rows: pd.DataFrame,
) -> pd.DataFrame:
    single = method_rows[
        method_rows["variant"] == "GRASP-VND seed 42"
    ][
        [
            "instance_id",
            "size",
            "known_optimum",
            "optimum",
            "feasible",
            "objective_value",
            "optimal",
            "runtime_total_seconds",
        ]
    ].rename(
        columns={
            "feasible": "single_feasible",
            "objective_value": "single_objective",
            "optimal": "single_optimal",
            "runtime_total_seconds": "single_runtime",
        }
    )
    best = method_rows[
        method_rows["variant"] == "GRASP-VND best-of-5"
    ][
        [
            "instance_id",
            "feasible",
            "objective_value",
            "optimal",
            "runtime_total_seconds",
        ]
    ].rename(
        columns={
            "feasible": "best5_feasible",
            "objective_value": "best5_objective",
            "optimal": "best5_optimal",
            "runtime_total_seconds": "best5_runtime",
        }
    )

    comparison = single.merge(best, on="instance_id")
    comparison["recovered"] = (
        ~comparison["single_feasible"]
        & comparison["best5_feasible"]
    )
    comparison["improved"] = (
        comparison["best5_feasible"]
        & (
            ~comparison["single_feasible"]
            | (
                comparison["best5_objective"]
                > comparison["single_objective"] + TOLERANCE
            )
        )
    )
    comparison["same_objective"] = (
        comparison["single_feasible"]
        & comparison["best5_feasible"]
        & (
            (
                comparison["best5_objective"]
                - comparison["single_objective"]
            ).abs()
            <= TOLERANCE
        )
    )
    comparison["new_optimum"] = (
        comparison["known_optimum"]
        & ~comparison["single_optimal"]
        & comparison["best5_optimal"]
    )
    comparison["runtime_ratio"] = (
        comparison["best5_runtime"]
        / comparison["single_runtime"]
    )
    return comparison


def effect_summary(
    local_effect: pd.DataFrame,
    multiseed_effect: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for scope in ["overall", *SIZE_ORDER]:
        local = (
            local_effect
            if scope == "overall"
            else local_effect[local_effect["size"] == scope]
        )
        multi = (
            multiseed_effect
            if scope == "overall"
            else multiseed_effect[
                multiseed_effect["size"] == scope
            ]
        )

        rows.append(
            {
                "scope": scope,
                "comparison": "Greedy -> Greedy + 1-swap",
                "instances": len(local),
                "recovered_instances": int(
                    local["recovered"].sum()
                ),
                "improved_instances": int(
                    local["improved"].sum()
                ),
                "equal_instances": int(local["equal"].sum()),
                "worsened_instances": int(
                    local["worsened"].sum()
                ),
                "new_optimal_instances": pd.NA,
                "runtime_ratio_mean": local[
                    "runtime_ratio"
                ].mean(),
            }
        )
        rows.append(
            {
                "scope": scope,
                "comparison": "H2 seed 42 -> H2 best-of-5",
                "instances": len(multi),
                "recovered_instances": int(
                    multi["recovered"].sum()
                ),
                "improved_instances": int(
                    multi["improved"].sum()
                ),
                "equal_instances": int(
                    multi["same_objective"].sum()
                ),
                "worsened_instances": 0,
                "new_optimal_instances": int(
                    multi["new_optimum"].sum()
                ),
                "runtime_ratio_mean": multi[
                    "runtime_ratio"
                ].mean(),
            }
        )

    return pd.DataFrame(rows)


def main() -> int:
    args = parse_arguments()

    heuristics = pd.read_csv(args.heuristics)
    grasp = pd.read_csv(args.grasp_vnd)
    exact = pd.read_csv(args.exact)

    validate_inputs(heuristics, grasp, exact, args.seed)

    method_rows = build_method_rows(
        heuristics,
        grasp,
        exact,
        args.seed,
    )
    summary = build_ablation_summary(method_rows)
    local_effect = build_local_search_effect(method_rows)
    multiseed_effect = build_multiseed_effect(method_rows)
    effects = effect_summary(local_effect, multiseed_effect)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    method_rows.to_csv(
        args.output_dir / "ablation_instance_detail.csv",
        index=False,
    )
    summary.to_csv(
        args.output_dir / "ablation_summary.csv",
        index=False,
    )
    local_effect.to_csv(
        args.output_dir / "local_search_effect.csv",
        index=False,
    )
    multiseed_effect.to_csv(
        args.output_dir / "multiseed_effect.csv",
        index=False,
    )
    effects.to_csv(
        args.output_dir / "component_effect_summary.csv",
        index=False,
    )

    overall = summary[summary["scope"] == "overall"]

    print("\n=== ABLATION MINIMA ===")
    print(
        overall[
            [
                "variant",
                "feasible_instances",
                "known_optimum_instances",
                "optimal_instances",
                "gap_mean_percent",
                "runtime_mean_seconds",
            ]
        ].to_string(index=False)
    )
    print("\n=== EFFETTO DEI COMPONENTI ===")
    print(
        effects[effects["scope"] == "overall"].to_string(
            index=False
        )
    )
    print(f"\nOutput: {args.output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
