"""Verifica l'upper bound di GRASP-VND su tutte le istanze pilota."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.core.instance import ProblemInstance  # noqa: E402
from cmmoflp_nuclear_siting.heuristics.grasp_vnd import (  # noqa: E402
    GraspVndConfig,
    solve_grasp_vnd,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Esegue GRASP-VND sul pilot e distingue upper bound "
            "raggiunto da upper bound non tight."
        )
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "instances/generated/pilot/manifest.csv",
    )
    parser.add_argument(
        "--exact-results",
        type=Path,
        default=PROJECT_ROOT / "results/raw/pilot_exact.csv",
    )
    parser.add_argument("--starts", type=int, default=100)
    parser.add_argument("--time-limit", type=float, default=10.0)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def read_exact_objectives(path: Path) -> dict[str, float]:
    """Legge gli ottimi del modello compatto già calcolati."""

    objectives: dict[str, float] = {}

    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if (
                row.get("method") == "compact"
                and row.get("feasible", "").lower() == "true"
                and row.get("objective_value")
            ):
                objectives[row["instance_id"]] = float(
                    row["objective_value"]
                )

    return objectives


def main() -> int:
    args = parse_arguments()
    exact_objectives = read_exact_objectives(args.exact_results)

    with args.manifest.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        manifest = list(csv.DictReader(handle))

    results: list[dict[str, object]] = []

    for row in manifest:
        instance = ProblemInstance.from_json(
            PROJECT_ROOT / row["json_path"]
        )
        solution = solve_grasp_vnd(
            instance,
            GraspVndConfig(
                random_seed=args.seed,
                max_starts=args.starts,
                time_limit_seconds=args.time_limit,
            ),
        )

        metadata = solution.metadata
        objective = float(solution.objective_value)
        upper_bound = float(metadata["objective_upper_bound"])
        exact = exact_objectives.get(instance.name)
        certified = bool(
            metadata["optimality_certified_by_upper_bound"]
        )
        matches_exact = (
            exact is not None and abs(objective - exact) <= 1e-7
        )

        if certified:
            interpretation = "UB raggiunto: ottimo certificato"
        elif matches_exact:
            interpretation = "Ottimo trovato, ma UB non tight"
        else:
            interpretation = "Ottimalità non certificata"

        results.append(
            {
                "instance_id": instance.name,
                "objective": objective,
                "upper_bound": upper_bound,
                "exact": exact,
                "certified": certified,
                "matches_exact": matches_exact,
                "starts": int(metadata["starts_completed"]),
                "interpretation": interpretation,
            }
        )

    print("\n=== VERIFICA UPPER BOUND SUL PILOT ===")
    print(
        f"{'Istanza':36} "
        f"{'H2':>10} {'UB':>10} {'Esatto':>10} "
        f"{'Start':>6}  Interpretazione"
    )
    print("-" * 112)

    for result in results:
        exact_text = (
            f"{result['exact']:.4f}"
            if result["exact"] is not None
            else "n.d."
        )
        print(
            f"{result['instance_id']:36} "
            f"{result['objective']:10.4f} "
            f"{result['upper_bound']:10.4f} "
            f"{exact_text:>10} "
            f"{result['starts']:6d}  "
            f"{result['interpretation']}"
        )

    certified_count = sum(
        bool(result["certified"]) for result in results
    )
    exact_without_certificate = sum(
        bool(result["matches_exact"]) and not bool(result["certified"])
        for result in results
    )
    not_exact = sum(
        not bool(result["matches_exact"]) for result in results
    )

    print("\nRiepilogo:")
    print(
        "  Ottimi certificati direttamente dall'upper bound: "
        f"{certified_count}/{len(results)}"
    )
    print(
        "  Ottimi trovati ma con upper bound non tight: "
        f"{exact_without_certificate}/{len(results)}"
    )
    print(
        "  Risultati diversi dall'ottimo compatto: "
        f"{not_exact}/{len(results)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
