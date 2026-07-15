"""Pipeline multi-seed per l'euristica avanzata GRASP-VND."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Iterable

from ..core.instance import ProblemInstance
from ..core.validation import validate_solution
from ..heuristics.grasp_vnd import GraspVndConfig, solve_grasp_vnd


@dataclass(frozen=True)
class GraspVndExperimentResult:
    """Risultato di una esecuzione GRASP-VND su una istanza."""

    instance_id: str
    class_id: str
    size: str
    distribution: str
    capacity_level: str
    instance_seed: int
    algorithm_seed: int
    method: str
    status: str
    feasible: bool
    objective_value: float | None
    runtime_seconds: float
    time_to_best_seconds: float | None
    open_sites: str
    starts_attempted: int
    starts_completed: int
    successful_starts: int
    failed_starts: int
    repair_attempts: int
    repair_successes: int
    one_swap_moves: int
    two_swap_moves: int
    cache_hits: int
    cache_misses: int
    vnd_iterations: int
    objective_upper_bound: float | None
    upper_bound_reached: bool
    optimality_certified_by_upper_bound: bool
    error: str


def _normalize_seed(value: object) -> int:
    """Converte seed mancanti in -1."""

    if value is None or value == "":
        return -1
    return int(value)


def _metadata_int(metadata: dict[str, object], key: str) -> int:
    value = metadata.get(key, 0)
    return int(value) if value is not None else 0


def _metadata_float(
    metadata: dict[str, object],
    key: str,
) -> float | None:
    value = metadata.get(key)
    return None if value is None else float(value)


def run_grasp_vnd_once(
    instance: ProblemInstance,
    algorithm_seed: int,
    config_template: GraspVndConfig,
) -> GraspVndExperimentResult:
    """Esegue GRASP-VND una volta e normalizza il risultato."""

    config = GraspVndConfig(
        alpha=config_template.alpha,
        max_starts=config_template.max_starts,
        time_limit_seconds=config_template.time_limit_seconds,
        candidate_list_size=config_template.candidate_list_size,
        max_iterations_per_start=(
            config_template.max_iterations_per_start
        ),
        repair_node_limit=config_template.repair_node_limit,
        random_seed=algorithm_seed,
        safety_weight=config_template.safety_weight,
        secondary_open_limit=config_template.secondary_open_limit,
    )

    start = perf_counter()

    try:
        solution = solve_grasp_vnd(instance, config)
        measured_runtime = perf_counter() - start
        validation = validate_solution(instance, solution)
        metadata = solution.metadata

        feasible = validation.feasible
        status = "success" if feasible else "invalid"

        error = ""
        if not feasible:
            error = "; ".join(validation.errors)

        return GraspVndExperimentResult(
            instance_id=instance.name,
            class_id=str(instance.metadata.get("class_id", "")),
            size=str(instance.metadata.get("size", "")),
            distribution=str(
                instance.metadata.get("distribution", "")
            ),
            capacity_level=str(
                instance.metadata.get("capacity_level", "")
            ),
            instance_seed=_normalize_seed(
                instance.metadata.get("seed")
            ),
            algorithm_seed=algorithm_seed,
            method="grasp_vnd",
            status=status,
            feasible=feasible,
            objective_value=(
                float(solution.objective_value)
                if solution.objective_value is not None
                else None
            ),
            runtime_seconds=float(
                metadata.get(
                    "total_runtime_seconds",
                    measured_runtime,
                )
            ),
            time_to_best_seconds=_metadata_float(
                metadata,
                "time_to_best_seconds",
            ),
            open_sites=";".join(sorted(solution.open_sites)),
            starts_attempted=_metadata_int(
                metadata,
                "starts_attempted",
            ),
            starts_completed=_metadata_int(
                metadata,
                "starts_completed",
            ),
            successful_starts=_metadata_int(
                metadata,
                "successful_starts",
            ),
            failed_starts=_metadata_int(
                metadata,
                "failed_starts",
            ),
            repair_attempts=_metadata_int(
                metadata,
                "repair_attempts",
            ),
            repair_successes=_metadata_int(
                metadata,
                "repair_successes",
            ),
            one_swap_moves=_metadata_int(
                metadata,
                "one_swap_moves",
            ),
            two_swap_moves=_metadata_int(
                metadata,
                "two_swap_moves",
            ),
            cache_hits=_metadata_int(metadata, "cache_hits"),
            cache_misses=_metadata_int(metadata, "cache_misses"),
            vnd_iterations=_metadata_int(
                metadata,
                "vnd_iterations",
            ),
            objective_upper_bound=_metadata_float(
                metadata,
                "objective_upper_bound",
            ),
            upper_bound_reached=bool(
                metadata.get("upper_bound_reached", False)
            ),
            optimality_certified_by_upper_bound=bool(
                metadata.get(
                    "optimality_certified_by_upper_bound",
                    False,
                )
            ),
            error=error,
        )

    except Exception as exc:  # noqa: BLE001
        measured_runtime = perf_counter() - start

        return GraspVndExperimentResult(
            instance_id=instance.name,
            class_id=str(instance.metadata.get("class_id", "")),
            size=str(instance.metadata.get("size", "")),
            distribution=str(
                instance.metadata.get("distribution", "")
            ),
            capacity_level=str(
                instance.metadata.get("capacity_level", "")
            ),
            instance_seed=_normalize_seed(
                instance.metadata.get("seed")
            ),
            algorithm_seed=algorithm_seed,
            method="grasp_vnd",
            status="error",
            feasible=False,
            objective_value=None,
            runtime_seconds=measured_runtime,
            time_to_best_seconds=None,
            open_sites="",
            starts_attempted=0,
            starts_completed=0,
            successful_starts=0,
            failed_starts=0,
            repair_attempts=0,
            repair_successes=0,
            one_swap_moves=0,
            two_swap_moves=0,
            cache_hits=0,
            cache_misses=0,
            vnd_iterations=0,
            objective_upper_bound=None,
            upper_bound_reached=False,
            optimality_certified_by_upper_bound=False,
            error=str(exc),
        )


def run_grasp_vnd_manifest(
    project_root: Path,
    manifest_path: Path,
    output_path: Path,
    algorithm_seeds: Iterable[int],
    config_template: GraspVndConfig,
) -> list[GraspVndExperimentResult]:
    """Esegue GRASP-VND per ogni coppia istanza-seed."""

    seeds = list(algorithm_seeds)
    if not seeds:
        raise ValueError("Specificare almeno un seed algoritmico.")
    if len(set(seeds)) != len(seeds):
        raise ValueError("I seed algoritmici devono essere distinti.")

    with manifest_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        manifest_rows = list(csv.DictReader(handle))

    if not manifest_rows:
        raise ValueError("Il manifest non contiene istanze.")

    results: list[GraspVndExperimentResult] = []

    for row in manifest_rows:
        instance = ProblemInstance.from_json(
            project_root / row["json_path"]
        )
        instance.metadata.update(
            {
                "class_id": row.get("class_id", ""),
                "size": row.get("size", ""),
                "distribution": row.get("distribution", ""),
                "capacity_level": row.get("capacity_level", ""),
                "seed": _normalize_seed(row.get("seed")),
            }
        )

        for algorithm_seed in seeds:
            result = run_grasp_vnd_once(
                instance=instance,
                algorithm_seed=algorithm_seed,
                config_template=config_template,
            )
            results.append(result)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(result) for result in results]

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
        )
        writer.writeheader()
        writer.writerows(rows)

    return results
