"""Valida un'istanza JSON e stampa un riepilogo."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.core.instance import ProblemInstance  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida un'istanza CMMOFLP.")
    parser.add_argument("instance", type=Path)
    args = parser.parse_args()

    try:
        instance = ProblemInstance.from_json(args.instance)
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print(f"Errore: {exc}")
        return 1

    total_demand = sum(x.demand for x in instance.communities)
    capacities = sorted((x.capacity for x in instance.sites), reverse=True)
    best_p_capacity = sum(capacities[: instance.p])

    print(f"Istanza: {instance.name}")
    print(f"Comunità: {len(instance.communities)}")
    print(f"Siti candidati: {len(instance.sites)}")
    print(f"Centrali da aprire: {instance.p}")
    print(f"Domanda totale: {total_demand:.2f}")
    print(f"Capacità massima con p siti: {best_p_capacity:.2f}")
    print("Validazione completata con successo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
