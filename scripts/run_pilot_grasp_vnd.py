"""Esegue GRASP-VND multi-seed sulle istanze pilota."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.experiments.grasp_vnd_runner import (  # noqa: E402
    run_grasp_vnd_manifest,
)
from cmmoflp_nuclear_siting.heuristics.grasp_vnd import (  # noqa: E402
    GraspVndConfig,
)


DEFAULT_SEEDS = [42, 123, 2026, 31415, 98765]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Esegue GRASP-VND multi-seed sul pilot."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "instances/generated/pilot/manifest.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "results/raw/pilot_grasp_vnd.csv",
    )
    parser.add_argument(
        "--algorithm-seeds",
        type=int,
        nargs="+",
        default=DEFAULT_SEEDS,
    )
    parser.add_argument("--starts", type=int, default=100)
    parser.add_argument("--time-limit", type=float, default=10.0)
    parser.add_argument("--alpha", type=float, default=0.30)
    parser.add_argument("--candidate-list-size", type=int, default=20)
    parser.add_argument("--safety-weight", type=float, default=0.80)
    parser.add_argument("--secondary-open-limit", type=int, default=3)
    parser.add_argument("--repair-node-limit", type=int, default=100_000)
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    config = GraspVndConfig(
        alpha=args.alpha,
        max_starts=args.starts,
        time_limit_seconds=args.time_limit,
        candidate_list_size=args.candidate_list_size,
        repair_node_limit=args.repair_node_limit,
        safety_weight=args.safety_weight,
        secondary_open_limit=args.secondary_open_limit,
    )

    results = run_grasp_vnd_manifest(
        project_root=PROJECT_ROOT,
        manifest_path=args.manifest,
        output_path=args.output,
        algorithm_seeds=args.algorithm_seeds,
        config_template=config,
    )

    feasible = [result for result in results if result.feasible]
    errors = [result for result in results if result.status == "error"]
    certified = [
        result
        for result in results
        if result.optimality_certified_by_upper_bound
    ]

    average_runtime = (
        sum(result.runtime_seconds for result in results)
        / len(results)
    )
    average_time_to_best = (
        sum(
            result.time_to_best_seconds or 0.0
            for result in feasible
        )
        / len(feasible)
        if feasible
        else 0.0
    )

    print("\n=== PILOT GRASP-VND MULTI-SEED ===")
    print(f"Istanze: {len(results) // len(args.algorithm_seeds)}")
    print(f"Seed algoritmici: {len(args.algorithm_seeds)}")
    print(f"Esecuzioni complessive: {len(results)}")
    print(f"Soluzioni ammissibili: {len(feasible)}")
    print(f"Ottimi certificati dall'upper bound: {len(certified)}")
    print(f"Errori: {len(errors)}")
    print(f"Tempo medio totale: {average_runtime:.6f} s")
    print(f"Tempo medio al best: {average_time_to_best:.6f} s")
    print(f"File CSV: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
