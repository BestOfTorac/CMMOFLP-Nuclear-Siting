"""Unione controllata dei manifest di istanze."""

from __future__ import annotations

import csv
from pathlib import Path


def merge_manifests(
    input_paths: list[Path],
    output_path: Path,
) -> list[dict[str, str]]:
    """Unisce manifest compatibili preservando l'ordine degli input."""

    if not input_paths:
        raise ValueError("Specificare almeno un manifest da unire.")

    all_rows: list[dict[str, str]] = []
    fieldnames: list[str] | None = None
    seen_instance_ids: set[str] = set()

    for input_path in input_paths:
        with input_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)

        if reader.fieldnames is None:
            raise ValueError(
                f"Il manifest {input_path} non contiene intestazioni."
            )

        current_fields = list(reader.fieldnames)

        if fieldnames is None:
            fieldnames = current_fields
        elif current_fields != fieldnames:
            raise ValueError(
                "I manifest non hanno le stesse colonne: "
                f"{input_path}"
            )

        for row in rows:
            instance_id = row.get("instance_id", "").strip()

            if not instance_id:
                raise ValueError(
                    f"Riga senza instance_id nel manifest {input_path}."
                )
            if instance_id in seen_instance_ids:
                raise ValueError(
                    f"instance_id duplicato: {instance_id}"
                )

            seen_instance_ids.add(instance_id)
            all_rows.append(row)

    if not all_rows:
        raise ValueError("I manifest non contengono istanze.")

    assert fieldnames is not None

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(all_rows)

    return all_rows
