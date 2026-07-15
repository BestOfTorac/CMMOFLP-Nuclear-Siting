"""Verifica locale dei due metodi esatti sulla toy instance."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.core.instance import ProblemInstance  # noqa: E402
from cmmoflp_nuclear_siting.exact.ampl_runner import (  # noqa: E402
    solve_with_ampl,
)


def main() -> int:
    instance = ProblemInstance.from_json(
        PROJECT_ROOT / "instances/test/toy_instance_01.json"
    )

    print("\n=== VERIFICA METODI ESATTI SULLA TOY INSTANCE ===")

    for method in ("compact", "threshold"):
        result = solve_with_ampl(
            instance=instance,
            method=method,
            project_root=PROJECT_ROOT,
            solver="gurobi",
            time_limit_seconds=300,
        )

        print(f"\nMetodo: {method}")
        print(f"  Stato: {result.status}")
        print(f"  Ammissibile: {result.feasible}")
        print(f"  Obiettivo: {result.objective_value}")
        print(f"  Siti aperti: {', '.join(result.open_sites)}")
        print(f"  Tempo end-to-end: {result.runtime_seconds:.6f} s")
        print(f"  Tempo solver: {result.solver_time_seconds}")

        if result.error:
            print(f"  Errore: {result.error}")

        if (
            not result.feasible
            or result.objective_value is None
            or abs(result.objective_value - 18.0278) > 1e-4
            or set(result.open_sites) != {"s1", "s4"}
        ):
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
