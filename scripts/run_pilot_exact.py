"""Esegue i metodi esatti AMPL sulle istanze pilota."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.exact.ampl_runner import (  # noqa: E402
    run_exact_manifest,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Esegue i metodi esatti AMPL sul pilot."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "instances/generated/pilot/manifest.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "results/raw/pilot_exact.csv",
    )
    parser.add_argument(
        "--methods",
        nargs="+",
        choices=["compact", "threshold"],
        default=["compact", "threshold"],
    )
    parser.add_argument(
        "--solver",
        default="gurobi",
    )
    parser.add_argument(
        "--time-limit",
        type=int,
        default=300,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    results = run_exact_manifest(
        project_root=PROJECT_ROOT,
        manifest_path=args.manifest,
        output_path=args.output,
        methods=args.methods,
        solver=args.solver,
        time_limit_seconds=args.time_limit,
    )

    print("\n=== RISULTATI METODI ESATTI SUL PILOT ===")
    print(f"Esecuzioni complessive: {len(results)}")
    print(f"File CSV: {args.output}")

    for method in args.methods:
        selected = [result for result in results if result.method == method]
        feasible = [result for result in selected if result.feasible]
        errors = [result for result in selected if result.status == "error"]

        average_runtime = (
            sum(result.runtime_seconds for result in selected) / len(selected)
        )
        average_solver_time = (
            sum(
                result.solver_time_seconds or 0.0
                for result in selected
            )
            / len(selected)
        )

        print(f"\nMetodo: {method}")
        print(f"  Esecuzioni: {len(selected)}")
        print(f"  Soluzioni disponibili: {len(feasible)}")
        print(f"  Errori: {len(errors)}")
        print(f"  Tempo medio end-to-end: {average_runtime:.6f} s")
        print(f"  Tempo solver medio: {average_solver_time:.6f} s")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
