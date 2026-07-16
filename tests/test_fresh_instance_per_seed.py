"""Test dell'indipendenza tra esecuzioni multi-seed."""

import json
from pathlib import Path

from cmmoflp_nuclear_siting.experiments.grasp_vnd_runner import (
    load_instance_for_experiment,
)


def test_each_seed_receives_a_fresh_instance(tmp_path: Path) -> None:
    instance_path = tmp_path / "instance.json"
    instance_path.write_text(
        json.dumps(
            {
                "name": "fresh_instance",
                "p": 1,
                "communities": [
                    {
                        "id": "c1",
                        "x": 0.0,
                        "y": 0.0,
                        "demand": 1.0,
                    }
                ],
                "sites": [
                    {
                        "id": "s1",
                        "x": 1.0,
                        "y": 0.0,
                        "capacity": 1.0,
                    }
                ],
                "metadata": {},
            }
        ),
        encoding="utf-8",
    )

    row = {
        "json_path": "instance.json",
        "class_id": "test_class",
        "size": "test",
        "distribution": "uniform",
        "capacity_level": "tight",
        "seed": "7",
    }

    first = load_instance_for_experiment(tmp_path, row)
    second = load_instance_for_experiment(tmp_path, row)

    assert first is not second
    assert first.communities is not second.communities
    assert first.sites is not second.sites

    first.metadata["mutated"] = True

    assert "mutated" not in second.metadata
    assert second.metadata["class_id"] == "test_class"
    assert second.metadata["seed"] == 7
