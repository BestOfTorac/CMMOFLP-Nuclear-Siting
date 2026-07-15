"""Calcola i gap delle euristiche rispetto al modello esatto."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.analysis.gaps import (  # noqa: E402
    save_gap_analysis,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Confronta euristiche e soluzione esatta."
    )
    parser.add_argument(
        "--heuristics",
        type=Path,
        default=PROJECT_ROOT / "results/raw/pilot_heuristics.csv",
    )
    parser.add_argument(
        "--exact",
        type=Path,
        default=PROJECT_ROOT / "results/raw/pilot_exact.csv",
    )
    parser.add_argument(
        "--reference-method",
        choices=["compact", "threshold"],
        default="compact",
    )
    parser.add_argument(
        "--pairwise-output",
        type=Path,
        default=PROJECT_ROOT / "results/aggregated/heuristic_gaps.csv",
    )
    parser.add_argument(
        "--class-output",
        type=Path,
        default=PROJECT_ROOT / "results/aggregated/heuristic_gaps_by_class.csv",
    )
    return parser.parse_args()


def _format_optional(value: float | None, digits: int = 4) -> str:
    if value is None:
        return "n.d."
    return f"{value:.{digits}f}"


def main() -> int:
    args = parse_arguments()

    _, class_summary, summary = save_gap_analysis(
        heuristic_results_path=args.heuristics,
        exact_results_path=args.exact,
        pairwise_output_path=args.pairwise_output,
        class_output_path=args.class_output,
        exact_method=args.reference_method,
    )

    print(
        "\n=== GAP DELLE EURISTICHE RISPETTO "
        f"A {args.reference_method.upper()} ==="
    )

    for method, values in summary.items():
        print(f"\nMetodo: {method}")
        print(f"  Esecuzioni: {values['runs']}")
        print(f"  Soluzioni ammissibili: {values['feasible_runs']}")
        print(f"  Confronti disponibili: {values['comparable_runs']}")
        print(f"  Soluzioni ottime: {values['optimal_matches']}")
        print(f"  Soluzioni subottime: {values['suboptimal_runs']}")
        print(f"  Fallimenti: {values['failed_runs']}")
        print(
            "  Gap medio: "
            f"{_format_optional(values['average_gap_percent'])}%"
        )
        print(
            "  Gap mediano: "
            f"{_format_optional(values['median_gap_percent'])}%"
        )
        print(
            "  Gap massimo: "
            f"{_format_optional(values['maximum_gap_percent'])}%"
        )
        print(
            "  Speedup medio rispetto all'esatto: "
            f"{_format_optional(values['average_speedup_vs_exact'], 2)}x"
        )

    print(f"\nRighe aggregate per classe: {len(class_summary)}")
    print(f"Confronto per istanza: {args.pairwise_output}")
    print(f"Aggregazione per classe: {args.class_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
