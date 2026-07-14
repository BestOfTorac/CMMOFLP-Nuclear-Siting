"""Esegue la local search sulla toy instance."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.core.instance import ProblemInstance  # noqa: E402
from cmmoflp_nuclear_siting.core.validation import validate_solution  # noqa: E402
from cmmoflp_nuclear_siting.heuristics.local_search import (  # noqa: E402
    solve_local_search,
)


def main() -> int:
    instance_path = PROJECT_ROOT / "instances/test/toy_instance_01.json"
    instance = ProblemInstance.from_json(instance_path)

    solution = solve_local_search(instance)
    validation = validate_solution(instance, solution)

    print("\n=== RISULTATO REPAIR + LOCAL SEARCH ===")
    print(f"Valore iniziale: {solution.metadata['initial_objective']:.4f}")
    print(f"Valore finale: {solution.objective_value:.4f}")
    print(f"Iterazioni migliorative: {solution.metadata['iterations']}")
    print(f"Centrali aperte: {', '.join(solution.open_sites)}")

    print("\nAssegnamenti:")
    for community_id in sorted(solution.assignments):
        print(f"  {community_id} -> {solution.assignments[community_id]}")

    print("\nValidazione:")
    print(f"  Soluzione ammissibile: {validation.feasible}")

    return 0 if validation.feasible else 1


if __name__ == "__main__":
    raise SystemExit(main())
