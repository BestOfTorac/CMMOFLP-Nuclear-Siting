"""GRASP multi-start con VND e riparazione per il CMMOFLP."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import random
from time import perf_counter

from ..core.instance import ProblemInstance
from ..core.solution import Solution
from ..core.validation import validate_solution
from .greedy import (
    _assign_communities_best_fit,
    compute_site_safety,
)
from .local_search import solve_local_search
from .repair import find_feasible_assignment


Assignment = dict[str, str]
AssignmentCache = dict[frozenset[str], Assignment | None]
TOLERANCE = 1e-9


@dataclass(frozen=True)
class GraspVndConfig:
    """Parametri dell'euristica avanzata."""

    alpha: float = 0.30
    max_starts: int = 25
    max_starts_without_improvement: int = 20
    time_limit_seconds: float = 5.0
    candidate_list_size: int = 20
    max_iterations_per_start: int = 50
    repair_node_limit: int = 100_000
    random_seed: int = 42
    safety_weight: float = 0.80
    secondary_open_limit: int = 3


@dataclass
class SearchStatistics:
    """Contatori raccolti durante l'esecuzione."""

    starts_attempted: int = 0
    starts_completed: int = 0
    successful_starts: int = 0
    failed_starts: int = 0
    repair_attempts: int = 0
    repair_successes: int = 0
    one_swap_moves: int = 0
    two_swap_moves: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    vnd_iterations: int = 0
    stagnation_stops: int = 0
    deadline_stops: int = 0


def _validate_config(config: GraspVndConfig) -> None:
    if not 0.0 <= config.alpha <= 1.0:
        raise ValueError("alpha deve appartenere all'intervallo [0, 1].")
    if config.max_starts <= 0:
        raise ValueError("max_starts deve essere positivo.")
    if config.max_starts_without_improvement <= 0:
        raise ValueError(
            "max_starts_without_improvement deve essere positivo."
        )
    if config.time_limit_seconds <= 0:
        raise ValueError("Il time limit deve essere positivo.")
    if config.candidate_list_size < 2:
        raise ValueError("candidate_list_size deve essere almeno 2.")
    if config.max_iterations_per_start < 0:
        raise ValueError(
            "max_iterations_per_start non può essere negativo."
        )
    if config.repair_node_limit <= 0:
        raise ValueError("repair_node_limit deve essere positivo.")
    if not 0.0 <= config.safety_weight <= 1.0:
        raise ValueError(
            "safety_weight deve appartenere all'intervallo [0, 1]."
        )
    if config.secondary_open_limit <= 0:
        raise ValueError("secondary_open_limit deve essere positivo.")


def _check_deadline(deadline: float) -> None:
    if perf_counter() >= deadline:
        raise TimeoutError(
            "Il limite temporale di GRASP-VND è stato raggiunto."
        )


def _site_set_score(
    open_sites: list[str],
    safety: dict[str, float],
) -> tuple[float, float]:
    """Punteggio lessicografico: maximin e somma delle sicurezze."""

    return (
        min(safety[site_id] for site_id in open_sites),
        sum(safety[site_id] for site_id in open_sites),
    )


def _objective_upper_bound(
    instance: ProblemInstance,
    safety: dict[str, float],
) -> float:
    """Restituisce il bound del p-esimo sito più sicuro."""

    ordered_safety = sorted(safety.values(), reverse=True)
    return ordered_safety[instance.p - 1]


def _capacity_filter(
    instance: ProblemInstance,
    open_sites: list[str],
) -> bool:
    """Applica condizioni necessarie economiche di fattibilità."""

    capacity = {site.id: site.capacity for site in instance.sites}
    total_demand = sum(
        community.demand for community in instance.communities
    )
    largest_demand = max(
        community.demand for community in instance.communities
    )

    return (
        sum(capacity[site_id] for site_id in open_sites)
        + TOLERANCE
        >= total_demand
        and max(capacity[site_id] for site_id in open_sites)
        + TOLERANCE
        >= largest_demand
    )


def _copy_assignment(
    assignment: Assignment | None,
) -> Assignment | None:
    return None if assignment is None else assignment.copy()


def _assignment_for_sites(
    instance: ProblemInstance,
    open_sites: list[str],
    safety: dict[str, float],
    cache: AssignmentCache,
    statistics: SearchStatistics,
    repair_node_limit: int,
    deadline: float,
) -> Assignment | None:
    """Trova un assegnamento usando best-fit, repair e cache."""

    _check_deadline(deadline)
    key = frozenset(open_sites)

    if key in cache:
        statistics.cache_hits += 1
        return _copy_assignment(cache[key])

    statistics.cache_misses += 1

    if not _capacity_filter(instance, open_sites):
        cache[key] = None
        return None

    try:
        assignment = _assign_communities_best_fit(
            instance,
            open_sites,
            safety,
        )
        cache[key] = assignment.copy()
        return assignment
    except ValueError:
        statistics.repair_attempts += 1

    repaired = find_feasible_assignment(
        instance,
        open_sites,
        node_limit=repair_node_limit,
        deadline=deadline,
    )

    if repaired is not None:
        statistics.repair_successes += 1
        cache[key] = repaired.copy()
        return repaired

    cache[key] = None
    return None


def _normalized_scores(
    candidate_ids: list[str],
    values: dict[str, float],
) -> dict[str, float]:
    """Normalizza valori nell'intervallo [0, 1]."""

    minimum = min(values[site_id] for site_id in candidate_ids)
    maximum = max(values[site_id] for site_id in candidate_ids)

    if abs(maximum - minimum) <= 1e-12:
        return {site_id: 1.0 for site_id in candidate_ids}

    return {
        site_id: (
            values[site_id] - minimum
        ) / (
            maximum - minimum
        )
        for site_id in candidate_ids
    }


def _randomized_construction(
    instance: ProblemInstance,
    safety: dict[str, float],
    config: GraspVndConfig,
    rng: random.Random,
    cache: AssignmentCache,
    statistics: SearchStatistics,
    deadline: float,
) -> tuple[list[str], Assignment] | None:
    """Costruisce una soluzione tramite Restricted Candidate List."""

    capacity = {site.id: site.capacity for site in instance.sites}
    all_sites = sorted(site.id for site in instance.sites)
    total_demand = sum(
        community.demand for community in instance.communities
    )
    selected: list[str] = []

    while len(selected) < instance.p:
        _check_deadline(deadline)
        feasible_candidates: list[str] = []

        for candidate in all_sites:
            _check_deadline(deadline)

            if candidate in selected:
                continue

            trial = selected + [candidate]
            slots_left = instance.p - len(trial)
            remaining_capacities = sorted(
                (
                    capacity[site_id]
                    for site_id in all_sites
                    if site_id not in trial
                ),
                reverse=True,
            )
            maximum_reachable_capacity = (
                sum(capacity[site_id] for site_id in trial)
                + sum(remaining_capacities[:slots_left])
            )

            if (
                maximum_reachable_capacity + TOLERANCE
                >= total_demand
            ):
                feasible_candidates.append(candidate)

        if not feasible_candidates:
            return None

        safety_score = _normalized_scores(
            feasible_candidates,
            safety,
        )

        remaining_needed = max(
            0.0,
            total_demand
            - sum(capacity[site_id] for site_id in selected),
        )
        capacity_values = {
            site_id: (
                min(capacity[site_id], remaining_needed)
                if remaining_needed > 0
                else capacity[site_id]
            )
            for site_id in feasible_candidates
        }
        capacity_score = _normalized_scores(
            feasible_candidates,
            capacity_values,
        )

        combined_score = {
            site_id: (
                config.safety_weight * safety_score[site_id]
                + (1.0 - config.safety_weight)
                * capacity_score[site_id]
            )
            for site_id in feasible_candidates
        }

        best_score = max(combined_score.values())
        worst_score = min(combined_score.values())
        threshold = (
            best_score
            - config.alpha * (best_score - worst_score)
        )

        restricted_candidates = sorted(
            site_id
            for site_id in feasible_candidates
            if combined_score[site_id] + 1e-12 >= threshold
        )
        selected.append(rng.choice(restricted_candidates))

    selected.sort()
    assignment = _assignment_for_sites(
        instance,
        selected,
        safety,
        cache,
        statistics,
        config.repair_node_limit,
        deadline,
    )

    if assignment is None:
        return None

    return selected, assignment


def _incoming_candidates(
    instance: ProblemInstance,
    current_sites: list[str],
    safety: dict[str, float],
    limit: int,
    minimum_safety: float,
) -> list[str]:
    """Restituisce una lista mirata di siti chiusi promettenti."""

    capacity = {site.id: site.capacity for site in instance.sites}
    closed_sites = [
        site.id
        for site in instance.sites
        if site.id not in current_sites
        and safety[site.id] + TOLERANCE >= minimum_safety
    ]

    closed_sites.sort(
        key=lambda site_id: (
            -safety[site_id],
            -capacity[site_id],
            site_id,
        )
    )
    return closed_sites[:limit]


def _best_one_swap(
    instance: ProblemInstance,
    current_sites: list[str],
    current_score: tuple[float, float],
    safety: dict[str, float],
    config: GraspVndConfig,
    cache: AssignmentCache,
    statistics: SearchStatistics,
    deadline: float,
) -> tuple[list[str], Assignment, tuple[float, float]] | None:
    """Cerca il miglior 1-swap in un vicinato mirato."""

    outgoing = sorted(
        current_sites,
        key=lambda site_id: (safety[site_id], site_id),
    )[: min(config.secondary_open_limit, len(current_sites))]

    incoming = _incoming_candidates(
        instance,
        current_sites,
        safety,
        config.candidate_list_size,
        current_score[0],
    )

    best_sites: list[str] | None = None
    best_assignment: Assignment | None = None
    best_score = current_score

    for site_out in outgoing:
        for site_in in incoming:
            _check_deadline(deadline)

            candidate_sites = sorted(
                [
                    site_id
                    for site_id in current_sites
                    if site_id != site_out
                ]
                + [site_in]
            )
            candidate_score = _site_set_score(
                candidate_sites,
                safety,
            )

            if candidate_score[0] <= current_score[0] + TOLERANCE:
                continue
            if candidate_score <= best_score:
                continue

            assignment = _assignment_for_sites(
                instance,
                candidate_sites,
                safety,
                cache,
                statistics,
                config.repair_node_limit,
                deadline,
            )
            if assignment is None:
                continue

            best_sites = candidate_sites
            best_assignment = assignment
            best_score = candidate_score

    if best_sites is None or best_assignment is None:
        return None

    return best_sites, best_assignment, best_score


def _targeted_outgoing_pairs(
    current_sites: list[str],
    safety: dict[str, float],
    secondary_open_limit: int,
) -> list[tuple[str, str]]:
    """Costruisce le coppie uscenti usando i siti critici."""

    current_minimum = min(
        safety[site_id] for site_id in current_sites
    )
    critical = sorted(
        site_id
        for site_id in current_sites
        if safety[site_id] <= current_minimum + TOLERANCE
    )

    if len(critical) > 2:
        return []

    if len(critical) == 2:
        return [(critical[0], critical[1])]

    if len(critical) == 1:
        secondary = sorted(
            (
                site_id
                for site_id in current_sites
                if site_id not in critical
            ),
            key=lambda site_id: (safety[site_id], site_id),
        )[:secondary_open_limit]

        return [
            (critical[0], site_id)
            for site_id in secondary
        ]

    return []


def _best_two_swap(
    instance: ProblemInstance,
    current_sites: list[str],
    current_score: tuple[float, float],
    safety: dict[str, float],
    config: GraspVndConfig,
    cache: AssignmentCache,
    statistics: SearchStatistics,
    deadline: float,
) -> tuple[list[str], Assignment, tuple[float, float]] | None:
    """Cerca un 2-swap mirato sui siti critici."""

    if len(current_sites) < 2:
        return None

    outgoing_pairs = _targeted_outgoing_pairs(
        current_sites,
        safety,
        config.secondary_open_limit,
    )
    if not outgoing_pairs:
        return None

    incoming = _incoming_candidates(
        instance,
        current_sites,
        safety,
        config.candidate_list_size,
        current_score[0],
    )
    if len(incoming) < 2:
        return None

    best_sites: list[str] | None = None
    best_assignment: Assignment | None = None
    best_score = current_score

    for site_out_1, site_out_2 in outgoing_pairs:
        retained = [
            site_id
            for site_id in current_sites
            if site_id not in {site_out_1, site_out_2}
        ]

        for site_in_1, site_in_2 in combinations(incoming, 2):
            _check_deadline(deadline)

            candidate_sites = sorted(
                retained + [site_in_1, site_in_2]
            )
            candidate_score = _site_set_score(
                candidate_sites,
                safety,
            )

            if candidate_score[0] <= current_score[0] + TOLERANCE:
                continue
            if candidate_score <= best_score:
                continue

            assignment = _assignment_for_sites(
                instance,
                candidate_sites,
                safety,
                cache,
                statistics,
                config.repair_node_limit,
                deadline,
            )
            if assignment is None:
                continue

            best_sites = candidate_sites
            best_assignment = assignment
            best_score = candidate_score

    if best_sites is None or best_assignment is None:
        return None

    return best_sites, best_assignment, best_score


def _run_vnd(
    instance: ProblemInstance,
    initial_sites: list[str],
    initial_assignment: Assignment,
    safety: dict[str, float],
    config: GraspVndConfig,
    cache: AssignmentCache,
    statistics: SearchStatistics,
    deadline: float,
) -> tuple[list[str], Assignment, tuple[float, float]]:
    """Esegue VND: 1-swap, poi 2-swap mirato."""

    current_sites = sorted(initial_sites)
    current_assignment = initial_assignment.copy()
    current_score = _site_set_score(current_sites, safety)
    iterations = 0

    while iterations < config.max_iterations_per_start:
        if perf_counter() >= deadline:
            statistics.deadline_stops += 1
            break

        statistics.vnd_iterations += 1

        try:
            one_swap = _best_one_swap(
                instance,
                current_sites,
                current_score,
                safety,
                config,
                cache,
                statistics,
                deadline,
            )
        except TimeoutError:
            statistics.deadline_stops += 1
            break

        if one_swap is not None:
            (
                current_sites,
                current_assignment,
                current_score,
            ) = one_swap
            statistics.one_swap_moves += 1
            iterations += 1
            continue

        try:
            two_swap = _best_two_swap(
                instance,
                current_sites,
                current_score,
                safety,
                config,
                cache,
                statistics,
                deadline,
            )
        except TimeoutError:
            statistics.deadline_stops += 1
            break

        if two_swap is not None:
            (
                current_sites,
                current_assignment,
                current_score,
            ) = two_swap
            statistics.two_swap_moves += 1
            iterations += 1
            continue

        break

    return current_sites, current_assignment, current_score


def _build_solution(
    instance: ProblemInstance,
    open_sites: list[str],
    assignment: Assignment,
    safety: dict[str, float],
    config: GraspVndConfig,
    statistics: SearchStatistics,
    initial_objective: float,
    total_runtime_seconds: float,
    time_to_best_seconds: float,
    objective_upper_bound: float,
    stop_reason: str,
    starts_without_improvement: int,
) -> Solution:
    """Costruisce e valida la soluzione finale."""

    objective_value = min(
        safety[site_id] for site_id in open_sites
    )

    solution = Solution(
        open_sites=sorted(open_sites),
        assignments=assignment.copy(),
        objective_value=objective_value,
        metadata={
            "method": "grasp_vnd",
            "algorithm_seed": config.random_seed,
            "alpha": config.alpha,
            "max_starts": config.max_starts,
            "max_starts_without_improvement": (
                config.max_starts_without_improvement
            ),
            "time_limit_seconds": config.time_limit_seconds,
            "candidate_list_size": config.candidate_list_size,
            "starts_attempted": statistics.starts_attempted,
            "starts_completed": statistics.starts_completed,
            "successful_starts": statistics.successful_starts,
            "failed_starts": statistics.failed_starts,
            "starts_without_improvement": starts_without_improvement,
            "repair_attempts": statistics.repair_attempts,
            "repair_successes": statistics.repair_successes,
            "one_swap_moves": statistics.one_swap_moves,
            "two_swap_moves": statistics.two_swap_moves,
            "cache_hits": statistics.cache_hits,
            "cache_misses": statistics.cache_misses,
            "vnd_iterations": statistics.vnd_iterations,
            "stagnation_stops": statistics.stagnation_stops,
            "deadline_stops": statistics.deadline_stops,
            "stop_reason": stop_reason,
            "initial_objective": initial_objective,
            "objective_upper_bound": objective_upper_bound,
            "upper_bound_reached": (
                objective_value
                >= objective_upper_bound - TOLERANCE
            ),
            "optimality_certified_by_upper_bound": (
                objective_value
                >= objective_upper_bound - TOLERANCE
            ),
            "time_to_best_seconds": time_to_best_seconds,
            "total_runtime_seconds": total_runtime_seconds,
            "site_safety": safety,
        },
    )

    validation = validate_solution(instance, solution)
    if not validation.feasible:
        raise ValueError(
            "La soluzione GRASP-VND non è ammissibile: "
            + "; ".join(validation.errors)
        )

    return solution


def improve_with_vnd(
    instance: ProblemInstance,
    initial_sites: list[str],
    config: GraspVndConfig | None = None,
) -> Solution:
    """Applica il VND a un insieme iniziale di siti specificato."""

    config = config or GraspVndConfig(max_starts=1)
    _validate_config(config)
    instance.validate()

    start_time = perf_counter()
    deadline = start_time + config.time_limit_seconds
    safety = compute_site_safety(instance)
    objective_upper_bound = _objective_upper_bound(instance, safety)
    cache: AssignmentCache = {}
    statistics = SearchStatistics(
        starts_attempted=1,
        starts_completed=1,
    )

    assignment = _assignment_for_sites(
        instance,
        sorted(initial_sites),
        safety,
        cache,
        statistics,
        config.repair_node_limit,
        deadline,
    )
    if assignment is None:
        raise ValueError(
            "L'insieme iniziale di siti non ammette un assegnamento."
        )

    statistics.successful_starts = 1
    initial_objective = min(
        safety[site_id] for site_id in initial_sites
    )

    best_sites, best_assignment, _ = _run_vnd(
        instance,
        sorted(initial_sites),
        assignment,
        safety,
        config,
        cache,
        statistics,
        deadline,
    )

    runtime = perf_counter() - start_time
    objective = min(safety[site_id] for site_id in best_sites)

    if objective >= objective_upper_bound - TOLERANCE:
        stop_reason = "upper_bound"
    elif perf_counter() >= deadline:
        stop_reason = "time_limit"
    else:
        stop_reason = "local_optimum"

    return _build_solution(
        instance,
        best_sites,
        best_assignment,
        safety,
        config,
        statistics,
        initial_objective,
        runtime,
        runtime,
        objective_upper_bound,
        stop_reason,
        0,
    )


def solve_grasp_vnd(
    instance: ProblemInstance,
    config: GraspVndConfig | None = None,
) -> Solution:
    """Esegue GRASP multi-start con repair, VND e stagnazione."""

    config = config or GraspVndConfig()
    _validate_config(config)
    instance.validate()

    start_time = perf_counter()
    deadline = start_time + config.time_limit_seconds
    rng = random.Random(config.random_seed)
    safety = compute_site_safety(instance)
    objective_upper_bound = _objective_upper_bound(instance, safety)
    cache: AssignmentCache = {}
    statistics = SearchStatistics()

    best_sites: list[str] | None = None
    best_assignment: Assignment | None = None
    best_score: tuple[float, float] | None = None
    time_to_best = 0.0
    initial_objective = 0.0
    starts_without_improvement = 0
    stop_reason = "max_starts"

    statistics.starts_attempted += 1
    try:
        baseline = solve_local_search(
            instance,
            max_iterations=config.max_iterations_per_start,
            repair_node_limit=config.repair_node_limit,
            deadline=deadline,
        )
        statistics.starts_completed += 1
        statistics.successful_starts += 1

        baseline_sites = sorted(baseline.open_sites)
        baseline_assignment = baseline.assignments.copy()
        initial_objective = float(
            baseline.objective_value
            if baseline.objective_value is not None
            else 0.0
        )

        best_sites, best_assignment, best_score = _run_vnd(
            instance,
            baseline_sites,
            baseline_assignment,
            safety,
            config,
            cache,
            statistics,
            deadline,
        )
        time_to_best = perf_counter() - start_time
    except TimeoutError:
        statistics.deadline_stops += 1
        stop_reason = "time_limit"
    except ValueError:
        statistics.starts_completed += 1
        statistics.failed_starts += 1

    for _ in range(1, config.max_starts):
        if (
            best_score is not None
            and best_score[0]
            >= objective_upper_bound - TOLERANCE
        ):
            stop_reason = "upper_bound"
            break

        if perf_counter() >= deadline:
            statistics.deadline_stops += 1
            stop_reason = "time_limit"
            break

        if (
            starts_without_improvement
            >= config.max_starts_without_improvement
        ):
            statistics.stagnation_stops += 1
            stop_reason = "stagnation"
            break

        statistics.starts_attempted += 1

        try:
            constructed = _randomized_construction(
                instance,
                safety,
                config,
                rng,
                cache,
                statistics,
                deadline,
            )
        except TimeoutError:
            statistics.deadline_stops += 1
            stop_reason = "time_limit"
            break

        statistics.starts_completed += 1

        if constructed is None:
            statistics.failed_starts += 1
            starts_without_improvement += 1
            continue

        statistics.successful_starts += 1
        initial_sites, assignment = constructed

        candidate_sites, candidate_assignment, candidate_score = (
            _run_vnd(
                instance,
                initial_sites,
                assignment,
                safety,
                config,
                cache,
                statistics,
                deadline,
            )
        )

        primary_improved = (
            best_score is None
            or candidate_score[0] > best_score[0] + TOLERANCE
        )

        if best_score is None or candidate_score > best_score:
            best_sites = candidate_sites
            best_assignment = candidate_assignment
            best_score = candidate_score
            time_to_best = perf_counter() - start_time

        if primary_improved:
            starts_without_improvement = 0
        else:
            starts_without_improvement += 1

        if perf_counter() >= deadline:
            stop_reason = "time_limit"
            break

        if (
            best_score is not None
            and best_score[0]
            >= objective_upper_bound - TOLERANCE
        ):
            stop_reason = "upper_bound"
            break
    else:
        stop_reason = "max_starts"

    if (
        best_sites is None
        or best_assignment is None
        or best_score is None
    ):
        raise ValueError(
            "GRASP-VND non ha trovato alcuna soluzione ammissibile."
        )

    total_runtime = perf_counter() - start_time

    return _build_solution(
        instance,
        best_sites,
        best_assignment,
        safety,
        config,
        statistics,
        initial_objective,
        total_runtime,
        time_to_best,
        objective_upper_bound,
        stop_reason,
        starts_without_improvement,
    )
