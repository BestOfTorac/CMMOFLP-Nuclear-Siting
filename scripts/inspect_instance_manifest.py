"""Ispeziona dimensione e complessità di un manifest di istanze."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.analysis.instance_complexity import (  # noqa: E402
    ManifestComplexity,
    read_manifest_complexities,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stima la complessità delle istanze del manifest."
    )
    parser.add_argument(
        "manifest",
        type=Path,
        help="Percorso del manifest.csv.",
    )
    return parser.parse_args()


def _print_complexities(
    complexities: list[ManifestComplexity],
) -> None:
    print("\n=== COMPLESSITÀ STRUTTURALE DEL BENCHMARK ===")
    print(f"Istanze: {len(complexities)}")
    print(
        f"{'Istanza':40} {'|I|':>6} {'|J|':>6} {'p':>4} "
        f"{'Bin.':>10} {'Vincoli':>10} {'Solve soglia':>12}"
    )
    print("-" * 96)

    for item in complexities:
        print(
            f"{item.instance_id:40} "
            f"{item.communities:6d} "
            f"{item.candidate_sites:6d} "
            f"{item.plants_to_open:4d} "
            f"{item.binary_variables:10d} "
            f"{item.constraints:10d} "
            f"{item.threshold_solves:12d}"
        )

    by_size: dict[str, list[ManifestComplexity]] = {}
    for item in complexities:
        by_size.setdefault(item.size, []).append(item)

    print("\nRiepilogo per dimensione:")
    for size, items in sorted(by_size.items()):
        representative = items[0]
        print(
            f"  {size}: {len(items)} istanze, "
            f"{representative.binary_variables} variabili binarie, "
            f"{representative.constraints} vincoli, "
            f"{representative.threshold_solves} solve del threshold"
        )


def main() -> int:
    args = parse_arguments()
    complexities = read_manifest_complexities(args.manifest)
    _print_complexities(complexities)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
