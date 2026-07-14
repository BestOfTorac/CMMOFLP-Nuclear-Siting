"""Test della pipeline degli esperimenti euristici."""

from pathlib import Path
import csv

import pytest

from cmmoflp_nuclear_siting.core.instance import ProblemInstance
from cmmoflp_nuclear_siting.experiments.runner import (
    read_manifest,
    run_manifest,
    run_method,
    summarize_results,
)


TOY_PATH = Path("instances/test/toy_instance_01.json")


def test_run_method_returns_feasible_greedy_result() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)

    result = run_method(instance, "greedy")

    assert result.status == "success"
    assert result.feasible
    assert result.objective_value == pytest.approx(
        18.0277563773,
        abs=1e-6,
    )
    assert result.runtime_seconds >= 0.0


def test_run_method_rejects_unknown_method() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)

    with pytest.raises(ValueError):
        run_method(instance, "unknown")


def test_run_manifest_writes_one_row_per_instance_and_method(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "manifest.csv"
    output_path = tmp_path / "results.csv"

    with manifest_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "instance_id",
                "class_id",
                "size",
                "distribution",
                "capacity_level",
                "seed",
                "json_path",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "instance_id": "toy_instance_01",
                "class_id": "toy",
                "size": "toy",
                "distribution": "manual",
                "capacity_level": "test",
                "seed": 0,
                "json_path": TOY_PATH.as_posix(),
            }
        )

    results = run_manifest(
        project_root=Path("."),
        manifest_path=manifest_path,
        output_path=output_path,
        methods=["greedy", "local_search"],
    )

    assert len(results) == 2
    assert output_path.exists()
    assert all(result.feasible for result in results)

    with output_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 2
    assert {row["method"] for row in rows} == {
        "greedy",
        "local_search",
    }


def test_summarize_results_groups_by_method() -> None:
    instance = ProblemInstance.from_json(TOY_PATH)
    results = [
        run_method(instance, "greedy"),
        run_method(instance, "local_search"),
    ]

    summary = summarize_results(results)

    assert set(summary) == {"greedy", "local_search"}
    assert summary["greedy"]["runs"] == 1
    assert summary["local_search"]["feasible_runs"] == 1
