"""Analizza i risultati pilota dei metodi esatti."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.analysis.exact import (  # noqa: E402
    save_exact_analysis,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analizza compact e threshold sul pilot."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "results/raw/pilot_exact.csv",
    )
    parser.add_argument(
        "--pairwise-output",
        type=Path,
        default=PROJECT_ROOT / "results/aggregated/exact_pairwise.csv",
    )
    parser.add_argument(
        "--class-output",
        type=Path,
        default=PROJECT_ROOT / "results/aggregated/exact_by_class.csv",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    _, class_summary, summary = save_exact_analysis(
        raw_results_path=args.input,
        pairwise_output_path=args.pairwise_output,
        class_output_path=args.class_output,
    )

    print("\n=== ANALISI COMPACT VS THRESHOLD ===")
    print(f"Istanze: {summary['instances']}")
    print(f"Risolte da entrambi: {summary['both_solved']}")
    print(f"Stesso obiettivo: {summary['same_objective']}")
    print(f"Stessi siti aperti: {summary['same_open_sites']}")
    print(
        "Massima differenza assoluta tra obiettivi: "
        f"{summary['max_absolute_objective_delta']:.12g}"
    )
    print(
        "Rapporto medio tempi threshold/compact: "
        f"{summary['average_runtime_ratio']:.3f}"
    )
    print(
        "Rapporto mediano tempi threshold/compact: "
        f"{summary['median_runtime_ratio']:.3f}"
    )
    print(
        "Rapporto medio tempi solver threshold/compact: "
        f"{summary['average_solver_ratio']:.3f}"
    )

    for method, values in summary["by_method"].items():
        print(f"\nMetodo: {method}")
        print(f"  Esecuzioni: {values['runs']}")
        print(f"  Risolte: {int(values['solved'])}")
        print(
            "  Tempo medio end-to-end: "
            f"{values['average_runtime_seconds']:.6f} s"
        )
        print(
            "  Tempo mediano end-to-end: "
            f"{values['median_runtime_seconds']:.6f} s"
        )
        print(
            "  Tempo solver medio: "
            f"{values['average_solver_time_seconds']:.6f} s"
        )

    print(f"\nRighe aggregate per classe: {len(class_summary)}")
    print(f"Confronto per istanza: {args.pairwise_output}")
    print(f"Aggregazione per classe: {args.class_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
