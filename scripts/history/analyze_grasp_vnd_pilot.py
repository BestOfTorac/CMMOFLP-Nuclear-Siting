"""Analizza il pilot multi-seed di GRASP-VND."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.analysis.grasp_vnd import (  # noqa: E402
    save_grasp_vnd_multi_seed_analysis,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analizza GRASP-VND su più seed."
    )
    parser.add_argument(
        "--grasp-results",
        type=Path,
        default=PROJECT_ROOT / "results/raw/pilot_grasp_vnd.csv",
    )
    parser.add_argument(
        "--exact-results",
        type=Path,
        default=PROJECT_ROOT / "results/raw/pilot_exact.csv",
    )
    parser.add_argument(
        "--seed-output",
        type=Path,
        default=(
            PROJECT_ROOT
            / "results/aggregated/grasp_vnd_by_seed.csv"
        ),
    )
    parser.add_argument(
        "--instance-output",
        type=Path,
        default=(
            PROJECT_ROOT
            / "results/aggregated/grasp_vnd_by_instance.csv"
        ),
    )
    parser.add_argument(
        "--class-output",
        type=Path,
        default=(
            PROJECT_ROOT
            / "results/aggregated/grasp_vnd_by_class.csv"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    _, per_instance, per_class, summary = (
        save_grasp_vnd_multi_seed_analysis(
            grasp_results_path=args.grasp_results,
            exact_results_path=args.exact_results,
            seed_output_path=args.seed_output,
            instance_output_path=args.instance_output,
            class_output_path=args.class_output,
        )
    )

    average_gap = summary["average_gap_percent"]
    maximum_gap = summary["maximum_gap_percent"]

    print("\n=== ANALISI GRASP-VND MULTI-SEED ===")
    print(f"Istanze: {summary['instances']}")
    print(f"Esecuzioni seed: {summary['seed_runs']}")
    print(f"Soluzioni ammissibili: {summary['feasible_runs']}")
    print(f"Soluzioni ottime: {summary['optimal_runs']}")
    print(f"Ottimi certificati: {summary['certified_runs']}")
    print(
        "Istanze ottime per tutti i seed: "
        f"{summary['instances_optimal_for_all_seeds']}"
    )
    print(
        "Istanze ammissibili per tutti i seed: "
        f"{summary['instances_feasible_for_all_seeds']}"
    )
    print(
        "Gap medio: "
        f"{average_gap:.6f}%"
        if average_gap is not None
        else "Gap medio: n.d."
    )
    print(
        "Gap massimo: "
        f"{maximum_gap:.6f}%"
        if maximum_gap is not None
        else "Gap massimo: n.d."
    )
    print(
        "Tempo medio totale: "
        f"{summary['average_runtime_seconds']:.6f} s"
    )
    print(
        "Tempo mediano totale: "
        f"{summary['median_runtime_seconds']:.6f} s"
    )
    print(
        "Tempo medio al best: "
        f"{summary['average_time_to_best_seconds']:.6f} s"
    )
    print(
        "Start medi completati: "
        f"{summary['average_starts_completed']:.2f}"
    )
    print(f"Righe per istanza: {len(per_instance)}")
    print(f"Righe per classe: {len(per_class)}")
    print(f"Risultati per seed: {args.seed_output}")
    print(f"Risultati per istanza: {args.instance_output}")
    print(f"Risultati per classe: {args.class_output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
