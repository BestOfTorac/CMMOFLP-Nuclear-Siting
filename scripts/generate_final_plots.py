"""Genera i grafici definitivi a partire dalle tabelle versionate."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ABLATION = PROJECT_ROOT / "results" / "final" / "ablation" / "ablation_summary.csv"
DEFAULT_H2_INSTANCES = PROJECT_ROOT / "results" / "final" / "summary" / "h2_instance_summary.csv"
DEFAULT_NONCERTIFIED = PROJECT_ROOT / "results" / "final" / "summary" / "noncertified_instances.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "results" / "plots" / "final"

VARIANT_ORDER = [
    "Greedy",
    "Greedy + 1-swap",
    "GRASP-VND seed 42",
    "GRASP-VND best-of-5",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera i grafici finali del benchmark CMMOFLP."
    )
    parser.add_argument("--ablation", type=Path, default=DEFAULT_ABLATION)
    parser.add_argument("--h2-instances", type=Path, default=DEFAULT_H2_INSTANCES)
    parser.add_argument("--noncertified", type=Path, default=DEFAULT_NONCERTIFIED)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def _save_figure(figure: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        path,
        dpi=200,
        bbox_inches="tight",
        metadata={"Software": "CMMOFLP Nuclear Siting 1.0.0"},
    )
    plt.close(figure)


def _overall_ablation(ablation: pd.DataFrame) -> pd.DataFrame:
    overall = ablation.loc[ablation["scope"] == "overall"].copy()
    overall["variant"] = pd.Categorical(
        overall["variant"], categories=VARIANT_ORDER, ordered=True
    )
    overall = overall.sort_values("variant")
    if overall["variant"].isna().any() or len(overall) != len(VARIANT_ORDER):
        raise ValueError("La tabella di ablation non contiene le quattro varianti attese.")
    return overall


def plot_solution_quality(ablation: pd.DataFrame, output_dir: Path) -> None:
    overall = _overall_ablation(ablation)
    positions = np.arange(len(overall))
    width = 0.38

    figure, axis = plt.subplots(figsize=(10, 5.8))
    feasible = axis.bar(
        positions - width / 2,
        overall["feasibility_rate_percent"],
        width,
        label="Ammissibilità (su 90)",
    )
    optimal = axis.bar(
        positions + width / 2,
        overall["optimal_rate_known_percent"],
        width,
        label="Ottimalità (su ottimi noti)",
    )

    labels = [
        "Greedy",
        "Greedy\n+ 1-swap",
        "GRASP-VND\nseed 42",
        "GRASP-VND\nbest-of-5",
    ]
    axis.set_xticks(positions, labels)
    axis.set_ylim(0, 108)
    axis.set_ylabel("Istanze risolte (%)")
    axis.set_title("Fattibilità e qualità delle varianti euristiche")
    axis.grid(axis="y", alpha=0.25)
    axis.legend(loc="lower right")

    feasible_counts = overall["feasible_instances"].astype(int).tolist()
    optimal_counts = overall["optimal_instances"].astype(int).tolist()
    for bar, count in zip(feasible, feasible_counts, strict=True):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.2,
            f"{count}/90",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    for bar, count in zip(optimal, optimal_counts, strict=True):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.2,
            f"{count}/89",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    figure.tight_layout()
    _save_figure(figure, output_dir / "solution_quality.png")


def plot_quality_runtime_tradeoff(ablation: pd.DataFrame, output_dir: Path) -> None:
    overall = _overall_ablation(ablation)

    figure, axis = plt.subplots(figsize=(9, 5.8))
    axis.scatter(
        overall["runtime_mean_seconds"],
        overall["gap_mean_percent"],
        s=90,
    )

    short_labels = {
        "Greedy": "Greedy",
        "Greedy + 1-swap": "Greedy + 1-swap",
        "GRASP-VND seed 42": "GRASP-VND seed 42",
        "GRASP-VND best-of-5": "GRASP-VND best-of-5",
    }
    offsets = {
        "Greedy": (6, 8),
        "Greedy + 1-swap": (6, -16),
        "GRASP-VND seed 42": (6, 8),
        "GRASP-VND best-of-5": (-125, 8),
    }
    for row in overall.itertuples(index=False):
        axis.annotate(
            short_labels[str(row.variant)],
            (row.runtime_mean_seconds, row.gap_mean_percent),
            xytext=offsets[str(row.variant)],
            textcoords="offset points",
            fontsize=9,
        )

    axis.set_xscale("log")
    axis.set_xlabel("Runtime medio per istanza (secondi, scala logaritmica)")
    axis.set_ylabel("Gap medio rispetto all’ottimo noto (%)")
    axis.set_title("Compromesso tra qualità della soluzione e tempo di calcolo")
    axis.grid(alpha=0.25)
    figure.tight_layout()
    _save_figure(figure, output_dir / "quality_runtime_tradeoff.png")


def plot_h2_optimality_by_class(h2_instances: pd.DataFrame, output_dir: Path) -> None:
    required = {"size", "distribution", "capacity_level", "known_optimum", "best_gap_percent"}
    missing = required.difference(h2_instances.columns)
    if missing:
        raise ValueError(f"Colonne mancanti nella sintesi H2: {sorted(missing)}")

    data = h2_instances.copy()
    data["known_optimum"] = data["known_optimum"].eq(True)
    data["optimal"] = data["known_optimum"] & data["best_gap_percent"].fillna(np.inf).abs().le(1e-9)

    grouped = (
        data.groupby(["size", "distribution", "capacity_level"], as_index=False)
        .agg(known=("known_optimum", "sum"), optimal=("optimal", "sum"))
    )
    grouped["rate"] = np.where(grouped["known"] > 0, 100 * grouped["optimal"] / grouped["known"], np.nan)

    size_order = {"medium": 0, "large": 1, "xlarge": 2}
    distribution_order = {"uniform": 0, "clustered": 1}
    capacity_order = {"loose": 0, "medium": 1, "tight": 2}
    grouped["sort_key"] = grouped.apply(
        lambda row: (
            size_order[str(row["size"])],
            distribution_order[str(row["distribution"])],
            capacity_order[str(row["capacity_level"])],
        ),
        axis=1,
    )
    grouped = grouped.sort_values("sort_key", ascending=False).reset_index(drop=True)

    size_labels = {"medium": "Medium", "large": "Large", "xlarge": "XLarge"}
    labels = [
        f"{size_labels[str(row.size)]} · {str(row.distribution).capitalize()} · {str(row.capacity_level).capitalize()}"
        for row in grouped.itertuples(index=False)
    ]

    figure, axis = plt.subplots(figsize=(10.5, 8.2))
    bars = axis.barh(labels, grouped["rate"])
    axis.set_xlim(0, 108)
    axis.set_xlabel("Ottimi trovati da GRASP-VND best-of-5 (%)")
    axis.set_title("Qualità di GRASP-VND nelle 18 classi del benchmark")
    axis.grid(axis="x", alpha=0.25)

    for bar, row in zip(bars, grouped.itertuples(index=False), strict=True):
        axis.text(
            min(bar.get_width() + 1.0, 104.5),
            bar.get_y() + bar.get_height() / 2,
            f"{int(row.optimal)}/{int(row.known)}",
            va="center",
            fontsize=8.5,
        )

    figure.tight_layout()
    _save_figure(figure, output_dir / "h2_optimality_by_class.png")


def plot_noncertified_case(noncertified: pd.DataFrame, output_dir: Path) -> None:
    if len(noncertified) != 1:
        raise ValueError("È attesa esattamente una istanza non certificata.")

    row = noncertified.iloc[0]
    labels = ["Incumbent compact", "Best GRASP-VND", "Best bound compact"]
    values = [row["compact_incumbent"], row["h2_best"], row["best_bound"]]

    figure, axis = plt.subplots(figsize=(8.5, 5.5))
    bars = axis.bar(labels, values)
    axis.set_ylabel("Distanza minima di sicurezza")
    axis.set_title(f"Caso non certificato: {row['instance_id']}")
    axis.grid(axis="y", alpha=0.25)

    for bar, value in zip(bars, values, strict=True):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.025,
            f"{value:.3f}",
            ha="center",
            va="bottom",
        )

    improvement = float(row["h2_vs_compact_incumbent_percent"])
    axis.text(
        0.5,
        -0.18,
        f"GRASP-VND migliora l’incumbent compact del {improvement:.2f}%, "
        "ma resta sotto il bound e non certifica l’ottimo.",
        transform=axis.transAxes,
        ha="center",
        fontsize=9,
    )
    figure.tight_layout()
    _save_figure(figure, output_dir / "noncertified_case.png")


def main() -> None:
    args = parse_args()
    ablation = pd.read_csv(args.ablation)
    h2_instances = pd.read_csv(args.h2_instances)
    noncertified = pd.read_csv(args.noncertified)

    plot_solution_quality(ablation, args.output_dir)
    plot_quality_runtime_tradeoff(ablation, args.output_dir)
    plot_h2_optimality_by_class(h2_instances, args.output_dir)
    plot_noncertified_case(noncertified, args.output_dir)

    print("\n=== GRAFICI FINALI ===")
    for filename in [
        "solution_quality.png",
        "quality_runtime_tradeoff.png",
        "h2_optimality_by_class.png",
        "noncertified_case.png",
    ]:
        print(args.output_dir / filename)


if __name__ == "__main__":
    main()
