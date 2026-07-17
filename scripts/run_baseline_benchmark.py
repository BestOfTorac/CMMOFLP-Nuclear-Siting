"""Esegue le baseline greedy e local search su un manifest di benchmark."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.experiments.runner import (  # noqa: E402
    METHODS,
    run_manifest,
    summarize_results,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Esegue gli esperimenti euristici del CMMOFLP."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=(
            PROJECT_ROOT
            / "instances/generated/final_benchmark/manifest.csv"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "results/raw/final_heuristics.csv",
    )
    parser.add_argument(
        "--methods",
        nargs="+",
        choices=sorted(METHODS),
        default=["greedy", "local_search"],
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    results = run_manifest(
        project_root=PROJECT_ROOT,
        manifest_path=args.manifest,
        output_path=args.output,
        methods=args.methods,
    )
    summary = summarize_results(results)

    print("\n=== RISULTATI BASELINE DEL BENCHMARK ===")
    print(f"Esecuzioni complessive: {len(results)}")
    print(f"File CSV: {args.output}")

    for method_name, values in summary.items():
        print(f"\nMetodo: {method_name}")
        print(f"  Esecuzioni: {values['runs']}")
        print(f"  Soluzioni ammissibili: {values['feasible_runs']}")
        print(f"  Errori: {values['errors']}")
        print(
            "  Tempo medio: "
            f"{values['average_runtime_seconds']:.6f} s"
        )
        average_objective = values["average_objective"]
        if average_objective is not None:
            print(
                "  Valore obiettivo medio: "
                f"{average_objective:.4f}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
