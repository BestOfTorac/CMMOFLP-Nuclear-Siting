"""Ispeziona dimensione e complessità di un manifest di istanze."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ManifestComplexity:
    """Stima strutturale del modello compatto per una istanza."""

    instance_id: str
    class_id: str
    size: str
    communities: int
    candidate_sites: int
    plants_to_open: int
    binary_variables: int
    continuous_variables: int
    constraints: int
    threshold_solves: int


def estimate_compact_complexity(
    instance_id: str,
    class_id: str,
    size: str,
    communities: int,
    candidate_sites: int,
    plants_to_open: int,
) -> ManifestComplexity:
    """Calcola numero di variabili e vincoli del modello compatto."""

    if communities <= 0:
        raise ValueError("Il numero di comunità deve essere positivo.")
    if candidate_sites <= 0:
        raise ValueError("Il numero di siti deve essere positivo.")
    if not 1 <= plants_to_open <= candidate_sites:
        raise ValueError(
            "Le centrali da aprire devono essere comprese tra 1 e i siti."
        )

    binary_variables = (
        communities * candidate_sites
        + candidate_sites
    )
    constraints = (
        1
        + communities
        + communities * candidate_sites
        + 2 * candidate_sites
    )

    return ManifestComplexity(
        instance_id=instance_id,
        class_id=class_id,
        size=size,
        communities=communities,
        candidate_sites=candidate_sites,
        plants_to_open=plants_to_open,
        binary_variables=binary_variables,
        continuous_variables=1,
        constraints=constraints,
        threshold_solves=candidate_sites,
    )


def read_manifest_complexities(
    manifest_path: Path,
) -> list[ManifestComplexity]:
    """Legge un manifest generato e restituisce le stime."""

    with manifest_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise ValueError("Il manifest non contiene istanze.")

    required = {
        "instance_id",
        "class_id",
        "size",
        "communities",
        "candidate_sites",
        "plants_to_open",
    }
    missing = sorted(required - set(rows[0]))
    if missing:
        raise ValueError(
            "Colonne mancanti nel manifest: " + ", ".join(missing)
        )

    return [
        estimate_compact_complexity(
            instance_id=str(row["instance_id"]),
            class_id=str(row["class_id"]),
            size=str(row["size"]),
            communities=int(row["communities"]),
            candidate_sites=int(row["candidate_sites"]),
            plants_to_open=int(row["plants_to_open"]),
        )
        for row in rows
    ]


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


def main() -> int:
    args = parse_arguments()
    complexities = read_manifest_complexities(args.manifest)

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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
