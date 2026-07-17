"""Genera una collezione di istanze a partire da un file YAML."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import shutil
import sys

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.generation.generator import (  # noqa: E402
    GenerationConfig,
    generate_instance,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera classi di istanze CMMOFLP."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=(
            PROJECT_ROOT
            / "configs/benchmark/final_benchmark.yaml"
        ),
        help="File YAML con la configurazione.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Cartella di destinazione. Di default usa instances/generated/<nome>.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Sovrascrive la cartella dell'esperimento se esiste.",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    required = {
        "experiment_name",
        "instances_per_class",
        "base_seed",
        "sizes",
        "distributions",
        "capacity_levels",
    }
    missing = sorted(required - set(data))
    if missing:
        raise ValueError(
            "Campi mancanti nella configurazione: " + ", ".join(missing)
        )

    return data


def prepare_output_directory(path: Path, overwrite: bool) -> None:
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise FileExistsError(
                f"La cartella {path} non è vuota. "
                "Usare --overwrite per rigenerarla."
            )
        shutil.rmtree(path)

    path.mkdir(parents=True, exist_ok=True)


def main() -> int:
    args = parse_arguments()
    config = load_config(args.config)

    experiment_name = str(config["experiment_name"])
    output_root = (
        args.output
        if args.output is not None
        else PROJECT_ROOT / "instances/generated" / experiment_name
    )
    prepare_output_directory(output_root, args.overwrite)

    manifest_rows: list[dict[str, object]] = []
    class_index = 0

    for size in config["sizes"]:
        size_name = str(size["name"])

        for distribution in config["distributions"]:
            for capacity_level, factor in config["capacity_levels"].items():
                class_id = (
                    f"{size_name}_{distribution}_{capacity_level}"
                )
                class_directory = (
                    output_root
                    / size_name
                    / str(distribution)
                    / str(capacity_level)
                )
                class_directory.mkdir(parents=True, exist_ok=True)

                for instance_index in range(
                    1,
                    int(config["instances_per_class"]) + 1,
                ):
                    seed = (
                        int(config["base_seed"])
                        + class_index * 10_000
                        + instance_index
                    )
                    instance_name = (
                        f"{class_id}_{instance_index:03d}"
                    )

                    generation_config = GenerationConfig(
                        name=instance_name,
                        communities=int(size["communities"]),
                        candidate_sites=int(size["candidate_sites"]),
                        plants_to_open=int(size["plants_to_open"]),
                        seed=seed,
                        distribution=str(distribution),
                        capacity_level=str(capacity_level),
                        capacity_factor=float(factor),
                    )
                    instance = generate_instance(generation_config)

                    json_path = class_directory / f"{instance_name}.json"
                    instance.to_json(json_path)

                    manifest_rows.append(
                        {
                            "instance_id": instance_name,
                            "class_id": class_id,
                            "size": size_name,
                            "communities": len(instance.communities),
                            "candidate_sites": len(instance.sites),
                            "plants_to_open": instance.p,
                            "distribution": distribution,
                            "capacity_level": capacity_level,
                            "capacity_factor": factor,
                            "seed": seed,
                            "json_path": json_path.relative_to(
                                PROJECT_ROOT
                            ).as_posix(),
                        }
                    )

                class_index += 1

    manifest_path = output_root / "manifest.csv"
    with manifest_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(manifest_rows[0]),
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"Esperimento: {experiment_name}")
    print(f"Istanze generate: {len(manifest_rows)}")
    print(f"Classi generate: {class_index}")
    print(f"Cartella: {output_root}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
