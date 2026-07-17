"""Esegue i metodi esatti AMPL sulle istanze di un manifest."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.exact.ampl_runner import (  # noqa: E402
    run_exact_manifest,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Esegue i metodi esatti AMPL."
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
        default=PROJECT_ROOT / "results/raw/final_exact.csv",
    )
    parser.add_argument(
        "--methods",
        nargs="+",
        choices=["compact", "threshold"],
        default=["compact"],
    )
    parser.add_argument("--solver", default="gurobi")
    parser.add_argument("--time-limit", type=int, default=60)
    return parser.parse_args()


def _mean_optional(values: list[float | None]) -> float | None:
    selected = [value for value in values if value is not None]
    if not selected:
        return None
    return sum(selected) / len(selected)


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

    print("\n=== RISULTATI METODI ESATTI ===")
    print(f"Esecuzioni complessive: {len(results)}")
    print(f"File CSV: {args.output}")

    for method in args.methods:
        selected = [result for result in results if result.method == method]
        incumbents = [
            result for result in selected if result.has_incumbent
        ]
        certified = [
            result for result in selected if result.optimality_certified
        ]
        errors = [result for result in selected if result.status == "error"]
        reasons = Counter(
            result.termination_reason for result in selected
        )

        average_runtime = sum(
            result.runtime_seconds for result in selected
        ) / len(selected)
        average_solver_time = _mean_optional(
            [result.solver_time_seconds for result in selected]
        )
        average_gap = _mean_optional(
            [result.relative_mip_gap for result in incumbents]
        )

        print(f"\nMetodo: {method}")
        print(f"  Esecuzioni: {len(selected)}")
        print(f"  Incumbent disponibili: {len(incumbents)}")
        print(f"  Ottimi certificati: {len(certified)}")
        print(f"  Errori: {len(errors)}")
        print(f"  Tempo medio end-to-end: {average_runtime:.6f} s")
        if average_solver_time is not None:
            print(
                "  Tempo solver medio: "
                f"{average_solver_time:.6f} s"
            )
        if average_gap is not None:
            print(
                "  MIP gap relativo medio: "
                f"{average_gap * 100.0:.6f}%"
            )
        print("  Motivi di terminazione:")
        for reason, count in sorted(reasons.items()):
            print(f"    {reason}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
