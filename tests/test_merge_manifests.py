"""Test dell'unione dei manifest."""

import csv
from pathlib import Path

import pytest

from cmmoflp_nuclear_siting.analysis.manifest_merge import (
    merge_manifests,
)


FIELDS = [
    "instance_id",
    "class_id",
    "size",
    "distribution",
    "capacity_level",
    "seed",
    "communities",
    "candidate_sites",
    "plants_to_open",
    "json_path",
]


def write_manifest(
    path: Path,
    rows: list[dict[str, str]],
) -> None:
    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def sample_row(instance_id: str) -> dict[str, str]:
    return {
        "instance_id": instance_id,
        "class_id": "xxlarge_uniform_tight",
        "size": "xxlarge",
        "distribution": "uniform",
        "capacity_level": "tight",
        "seed": "1",
        "communities": "1200",
        "candidate_sites": "300",
        "plants_to_open": "30",
        "json_path": f"instances/{instance_id}.json",
    }


def test_merge_manifests_preserves_rows(tmp_path: Path) -> None:
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    output = tmp_path / "merged.csv"

    write_manifest(first, [sample_row("a")])
    write_manifest(second, [sample_row("b")])

    rows = merge_manifests([first, second], output)

    assert [row["instance_id"] for row in rows] == ["a", "b"]
    assert output.exists()


def test_merge_manifests_rejects_duplicate_ids(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    output = tmp_path / "merged.csv"

    write_manifest(first, [sample_row("duplicate")])
    write_manifest(second, [sample_row("duplicate")])

    with pytest.raises(ValueError):
        merge_manifests([first, second], output)
