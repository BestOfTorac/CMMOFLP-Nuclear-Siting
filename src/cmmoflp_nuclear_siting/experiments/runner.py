"""Esecuzione e registrazione degli esperimenti euristici."""

from __future__ import annotations

from collections.abc import Callable, Iterable
import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

from ..core.instance import ProblemInstance
from ..core.solution import Solution
from ..core.validation import validate_solution
from ..heuristics.greedy import solve_greedy
from ..heuristics.local_search import solve_local_search


SolverFunction = Callable[[ProblemInstance], Solution]


METHODS: dict[str, SolverFunction] = {
    "greedy": solve_greedy,
    "local_search": solve_local_search,
}


@dataclass(frozen=True)
class ExperimentResult:
    """Risultato normalizzato di una singola esecuzione."""

    instance_id: str
    class_id: str
    size: str
    distribution: str
    capacity_level: str
    seed: int
    method: str
    status: str
    feasible: bool
    objective_value: float | None
    runtime_seconds: float
    open_sites: str
    iterations: int | None
    initial_objective: float | None
    error: str


def _normalize_seed(value: object) -> int:
    """Converte il seed in intero usando -1 quando è assente.

    Le istanze manuali, come la toy instance, possono avere ``seed=None``.
    """

    if value is None or value == "":
        return -1

    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Seed non valido: {value!r}") from exc


def run_method(
    instance: ProblemInstance,
    method_name: str,
) -> ExperimentResult:
    """Esegue un metodo su una singola istanza e misura il tempo."""

    try:
        solver = METHODS[method_name]
    except KeyError as exc:
        allowed = ", ".join(sorted(METHODS))
        raise ValueError(
            f"Metodo sconosciuto: {method_name}. Metodi ammessi: {allowed}."
        ) from exc

    seed = _normalize_seed(instance.metadata.get("seed"))
    start = perf_counter()

    try:
        solution = solver(instance)
        runtime_seconds = perf_counter() - start
        validation = validate_solution(instance, solution)

        metadata = solution.metadata
        iterations_raw = metadata.get("iterations")
        initial_raw = metadata.get("initial_objective")

        return ExperimentResult(
            instance_id=instance.name,
            class_id=str(instance.metadata.get("class_id", "")),
            size=str(instance.metadata.get("size", "")),
            distribution=str(instance.metadata.get("distribution", "")),
            capacity_level=str(instance.metadata.get("capacity_level", "")),
            seed=seed,
            method=method_name,
            status="success" if validation.feasible else "invalid",
            feasible=validation.feasible,
            objective_value=solution.objective_value,
            runtime_seconds=runtime_seconds,
            open_sites=";".join(sorted(solution.open_sites)),
            iterations=(
                int(iterations_raw)
                if iterations_raw is not None
                else None
            ),
            initial_objective=(
                float(initial_raw)
                if initial_raw is not None
                else None
            ),
            error="; ".join(validation.errors),
        )
    except Exception as exc:  # noqa: BLE001
        runtime_seconds = perf_counter() - start
        return ExperimentResult(
            instance_id=instance.name,
            class_id=str(instance.metadata.get("class_id", "")),
            size=str(instance.metadata.get("size", "")),
            distribution=str(instance.metadata.get("distribution", "")),
            capacity_level=str(instance.metadata.get("capacity_level", "")),
            seed=seed,
            method=method_name,
            status="error",
            feasible=False,
            objective_value=None,
            runtime_seconds=runtime_seconds,
            open_sites="",
            iterations=None,
            initial_objective=None,
            error=f"{type(exc).__name__}: {exc}",
        )


def read_manifest(
    manifest_path: Path,
) -> list[dict[str, str]]:
    """Legge il manifest CSV prodotto dal generatore."""

    with manifest_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise ValueError(f"Il manifest {manifest_path} è vuoto.")

    if "json_path" not in rows[0]:
        raise ValueError("Il manifest non contiene la colonna json_path.")

    return rows


def write_results(
    output_path: Path,
    results: Iterable[ExperimentResult],
) -> None:
    """Salva i risultati grezzi in formato CSV."""

    result_rows = [asdict(result) for result in results]
    if not result_rows:
        raise ValueError("Non ci sono risultati da salvare.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(result_rows[0]),
        )
        writer.writeheader()
        writer.writerows(result_rows)


def run_manifest(
    project_root: Path,
    manifest_path: Path,
    output_path: Path,
    methods: Iterable[str] = ("greedy", "local_search"),
) -> list[ExperimentResult]:
    """Esegue i metodi richiesti su tutte le istanze del manifest."""

    method_names = list(methods)
    if not method_names:
        raise ValueError("Specificare almeno un metodo.")

    for method_name in method_names:
        if method_name not in METHODS:
            allowed = ", ".join(sorted(METHODS))
            raise ValueError(
                f"Metodo sconosciuto: {method_name}. Metodi ammessi: {allowed}."
            )

    manifest_rows = read_manifest(manifest_path)
    results: list[ExperimentResult] = []

    for row in manifest_rows:
        instance_path = project_root / row["json_path"]
        instance = ProblemInstance.from_json(instance_path)

        # Il manifest contiene informazioni utili all'analisi che vengono
        # copiate nei metadati dell'istanza.
        instance.metadata.update(
            {
                "class_id": row.get("class_id", ""),
                "size": row.get("size", ""),
                "distribution": row.get("distribution", ""),
                "capacity_level": row.get("capacity_level", ""),
                "seed": _normalize_seed(row.get("seed")),
            }
        )

        for method_name in method_names:
            results.append(run_method(instance, method_name))

    write_results(output_path, results)
    return results


def summarize_results(
    results: Iterable[ExperimentResult],
) -> dict[str, dict[str, Any]]:
    """Calcola un riepilogo essenziale per metodo."""

    summary: dict[str, dict[str, Any]] = {}

    for result in results:
        current = summary.setdefault(
            result.method,
            {
                "runs": 0,
                "feasible_runs": 0,
                "errors": 0,
                "total_runtime_seconds": 0.0,
                "objective_sum": 0.0,
                "objective_count": 0,
            },
        )

        current["runs"] += 1
        current["total_runtime_seconds"] += result.runtime_seconds

        if result.feasible:
            current["feasible_runs"] += 1
        if result.status == "error":
            current["errors"] += 1
        if result.objective_value is not None:
            current["objective_sum"] += result.objective_value
            current["objective_count"] += 1

    for current in summary.values():
        current["average_runtime_seconds"] = (
            current["total_runtime_seconds"] / current["runs"]
        )
        current["average_objective"] = (
            current["objective_sum"] / current["objective_count"]
            if current["objective_count"]
            else None
        )

    return summary
