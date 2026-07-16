"""Stime strutturali per i benchmark CMMOFLP."""

from __future__ import annotations

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
    """Calcola variabili e vincoli del modello compatto.

    Variabili:
    - x[i,j]: |I||J| binarie;
    - y[j]: |J| binarie;
    - z: una continua.

    Vincoli:
    - apertura di p siti: 1;
    - assegnamento: |I|;
    - linking: |I||J|;
    - capacità: |J|;
    - definizione maximin: |J|.
    """

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
