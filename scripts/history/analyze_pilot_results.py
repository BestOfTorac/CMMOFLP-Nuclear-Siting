"""Analizza i risultati pilota delle euristiche."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.analysis.pilot import save_analysis  # noqa: E402


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analizza greedy e local search sul pilot."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "results/raw/pilot_heuristics.csv",
    )
    parser.add_argument(
        "--pairwise-output",
        type=Path,
        default=PROJECT_ROOT / "results/aggregated/pilot_pairwise.csv",
    )
    parser.add_argument(
        "--class-output",
        type=Path,
        default=PROJECT_ROOT / "results/aggregated/pilot_by_class.csv",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    comparison, class_summary, summary = save_analysis(
        raw_results_path=args.input,
        pairwise_output_path=args.pairwise_output,
        class_output_path=args.class_output,
    )

    print("\n=== ANALISI APPAIATA GREEDY VS LOCAL SEARCH ===")
    print(f"Istanze complessive: {summary['instances']}")
    print(f"Istanze riparate: {summary['repaired']}")
    print(f"Istanze migliorate: {summary['improved']}")
    print(f"Istanze con stesso obiettivo: {summary['equal']}")
    print(f"Istanze peggiorate: {summary['worse']}")
    print(f"Istanze fallite da entrambi: {summary['both_failed']}")
    print(
        "Delta obiettivo medio sulle istanze condivise: "
        f"{summary['average_objective_delta_on_shared']:.6f}"
    )
    print(
        "Rapporto medio tempi local/greedy: "
        f"{summary['average_runtime_ratio_on_shared']:.3f}"
    )

    repaired = comparison[comparison["comparison"] == "repaired"]
    if not repaired.empty:
        print("\nIstanze riparate dalla local search:")
        for row in repaired.itertuples(index=False):
            print(
                f"  {row.instance_id} "
                f"({row.class_id}) -> "
                f"obiettivo {row.local_search_objective_value:.4f}"
            )

    print(f"\nConfronto per istanza: {args.pairwise_output}")
    print(f"Aggregazione per classe: {args.class_output}")
    print(f"Righe aggregate per classe: {len(class_summary)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
