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
    starts_without_improvement: int
    max_starts_without_improvement: int
    repair_attempts: int
    repair_successes: int
    one_swap_moves: int
    two_swap_moves: int
    cache_hits: int
    cache_misses: int
    vnd_iterations: int
    stagnation_stops: int
    deadline_stops: int
    stop_reason: str
    objective_upper_bound: float | None
    upper_bound_reached: bool
    optimality_certified_by_upper_bound: bool
    error: str


@dataclass(frozen=True)
class FailureClassification:
    """Classificazione di una esecuzione terminata senza soluzione."""

    status: str
    stop_reason: str
    error: str


_NO_INCUMBENT_MESSAGE = (
    "GRASP-VND non ha trovato alcuna soluzione ammissibile."
)


def _normalize_seed(value: object) -> int:
    if value is None or value == "":
        return -1
    return int(value)


def load_instance_for_experiment(
    project_root: Path,
    row: dict[str, str],
) -> ProblemInstance:
    """Carica una copia indipendente dell'istanza per una singola run.

    Ogni coppia istanza-seed deve lavorare su un oggetto nuovo, così
    eventuali cache o modifiche interne non possono propagarsi alla run
    successiva.
    """

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
    return instance


def _metadata_int(metadata: dict[str, object], key: str) -> int:
    value = metadata.get(key, 0)
    return int(value) if value is not None else 0


def _metadata_float(
    metadata: dict[str, object],
    key: str,
) -> float | None:
    value = metadata.get(key)
    return None if value is None else float(value)


def classify_grasp_vnd_failure(
    exception: Exception,
    runtime_seconds: float,
    time_limit_seconds: float,
) -> FailureClassification:
    """Distingue un limite senza incumbent da un errore software.

    Le istanze generate sono costruite per essere ammissibili. Quando H2
    non trova alcuna soluzione e consuma quasi tutto il budget temporale,
    la terminazione viene classificata come time limit senza incumbent,
    non come errore del programma.
    """

    message = str(exception).strip()

    if (
        isinstance(exception, ValueError)
        and _NO_INCUMBENT_MESSAGE in message
    ):
        tolerance = max(0.05, 0.02 * time_limit_seconds)
        reached_deadline = (
            runtime_seconds
            >= max(0.0, time_limit_seconds - tolerance)
        )

        if reached_deadline:
            return FailureClassification(
                status="limit",
                stop_reason="time_limit_no_incumbent",
                error="",
            )

        return FailureClassification(
            status="no_incumbent",
            stop_reason="search_no_incumbent",
            error="",
        )

    return FailureClassification(
        status="error",
        stop_reason="error",
        error=message,
    )


def _empty_result(
    *,
    instance: ProblemInstance,
    algorithm_seed: int,
    config: GraspVndConfig,
    runtime_seconds: float,
    classification: FailureClassification,
) -> GraspVndExperimentResult:
    """Costruisce una riga senza soluzione, ma correttamente classificata."""

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
        status=classification.status,
        feasible=False,
        objective_value=None,
        runtime_seconds=runtime_seconds,
        time_to_best_seconds=None,
        open_sites="",
        starts_attempted=0,
        starts_completed=0,
        successful_starts=0,
        failed_starts=0,
        starts_without_improvement=0,
        max_starts_without_improvement=(
            config.max_starts_without_improvement
        ),
        repair_attempts=0,
        repair_successes=0,
        one_swap_moves=0,
        two_swap_moves=0,
        cache_hits=0,
        cache_misses=0,
        vnd_iterations=0,
        stagnation_stops=0,
        deadline_stops=(
            1
            if classification.stop_reason
            == "time_limit_no_incumbent"
            else 0
        ),
        stop_reason=classification.stop_reason,
        objective_upper_bound=None,
        upper_bound_reached=False,
        optimality_certified_by_upper_bound=False,
        error=classification.error,
    )


def run_grasp_vnd_once(
    instance: ProblemInstance,
    algorithm_seed: int,
    config_template: GraspVndConfig,
) -> GraspVndExperimentResult:
    """Esegue GRASP-VND una volta e normalizza il risultato."""

    config = GraspVndConfig(
        alpha=config_template.alpha,
        max_starts=config_template.max_starts,
        max_starts_without_improvement=(
            config_template.max_starts_without_improvement
        ),
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
        error = "" if feasible else "; ".join(validation.errors)

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
            starts_without_improvement=_metadata_int(
                metadata,
                "starts_without_improvement",
            ),
            max_starts_without_improvement=_metadata_int(
                metadata,
                "max_starts_without_improvement",
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
            stagnation_stops=_metadata_int(
                metadata,
                "stagnation_stops",
            ),
            deadline_stops=_metadata_int(
                metadata,
                "deadline_stops",
            ),
            stop_reason=str(metadata.get("stop_reason", "")),
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
        classification = classify_grasp_vnd_failure(
            exception=exc,
            runtime_seconds=measured_runtime,
            time_limit_seconds=config.time_limit_seconds,
        )

        return _empty_result(
            instance=instance,
            algorithm_seed=algorithm_seed,
            config=config,
            runtime_seconds=measured_runtime,
            classification=classification,
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
        for algorithm_seed in seeds:
            # Ogni esecuzione riceve una nuova istanza. Questo garantisce
            # indipendenza tra seed ed evita contaminazioni da cache o
            # mutazioni accidentali lasciate dalle run precedenti.
            instance = load_instance_for_experiment(
                project_root,
                row,
            )
            results.append(
                run_grasp_vnd_once(
                    instance=instance,
                    algorithm_seed=algorithm_seed,
                    config_template=config_template,
                )
            )

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
