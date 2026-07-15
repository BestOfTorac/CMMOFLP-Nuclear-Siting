"""Esegue GRASP-VND su una istanza JSON."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.core.instance import ProblemInstance  # noqa: E402
from cmmoflp_nuclear_siting.core.validation import validate_solution  # noqa: E402
from cmmoflp_nuclear_siting.heuristics.grasp_vnd import (  # noqa: E402
    GraspVndConfig,
    solve_grasp_vnd,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Esegue l'euristica GRASP-VND."
    )
    parser.add_argument(
        "--instance",
        type=Path,
        default=PROJECT_ROOT / "instances/test/toy_instance_01.json",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--starts", type=int, default=25)
    parser.add_argument("--alpha", type=float, default=0.30)
    parser.add_argument("--time-limit", type=float, default=5.0)
    parser.add_argument("--candidate-list-size", type=int, default=20)
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    instance = ProblemInstance.from_json(args.instance)

    config = GraspVndConfig(
        random_seed=args.seed,
        max_starts=args.starts,
        alpha=args.alpha,
        time_limit_seconds=args.time_limit,
        candidate_list_size=args.candidate_list_size,
    )
    solution = solve_grasp_vnd(instance, config)
    validation = validate_solution(instance, solution)
    metadata = solution.metadata

    print("\n=== RISULTATO GRASP + VND ===")
    print(f"Istanza: {instance.name}")
    print(f"Valore obiettivo: {solution.objective_value:.4f}")
    print(f"Centrali aperte: {', '.join(solution.open_sites)}")
    print(f"Soluzione ammissibile: {validation.feasible}")
    print(
        "Upper bound teorico: "
        f"{metadata['objective_upper_bound']:.4f}"
    )
    print(
        "Ottimalità certificata dall'upper bound: "
        f"{metadata['optimality_certified_by_upper_bound']}"
    )

    print("\nStatistiche:")
    print(f"  Seed: {metadata['algorithm_seed']}")
    print(f"  Start completati: {metadata['starts_completed']}")
    print(f"  Start ammissibili: {metadata['successful_starts']}")
    print(f"  Start falliti: {metadata['failed_starts']}")
    print(f"  Repair tentati: {metadata['repair_attempts']}")
    print(f"  Repair riusciti: {metadata['repair_successes']}")
    print(f"  Mosse 1-swap: {metadata['one_swap_moves']}")
    print(f"  Mosse 2-swap: {metadata['two_swap_moves']}")
    print(f"  Cache hit: {metadata['cache_hits']}")
    print(f"  Cache miss: {metadata['cache_misses']}")
    print(
        "  Tempo al best: "
        f"{metadata['time_to_best_seconds']:.6f} s"
    )
    print(
        "  Tempo totale: "
        f"{metadata['total_runtime_seconds']:.6f} s"
    )

    return 0 if validation.feasible else 1


if __name__ == "__main__":
    raise SystemExit(main())
