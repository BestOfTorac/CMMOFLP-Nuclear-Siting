"""Ricerca locale con riparazione per il CMMOFLP nucleare."""

from __future__ import annotations

from itertools import product
from time import perf_counter

from ..core.instance import ProblemInstance
from ..core.solution import Solution
from ..core.validation import validate_solution
from .greedy import (
    _select_sites_with_capacity_lookahead,
    compute_site_safety,
    solve_greedy,
)
from .repair import find_feasible_assignment


def _site_set_score(
    open_sites: list[str],
    safety: dict[str, float],
) -> tuple[float, float]:
    """Restituisce il punteggio lessicografico di un insieme di siti."""

    return (
        min(safety[site_id] for site_id in open_sites),
        sum(safety[site_id] for site_id in open_sites),
    )


def _deadline_reached(deadline: float | None) -> bool:
    return deadline is not None and perf_counter() >= deadline


def _build_solution(
    instance: ProblemInstance,
    open_sites: list[str],
    assignments: dict[str, str],
    safety: dict[str, float],
    iterations: int,
    initial_objective: float,
    deadline_reached: bool,
) -> Solution:
    """Costruisce e valida un oggetto Solution."""

    objective_value = min(safety[site_id] for site_id in open_sites)

    solution = Solution(
        open_sites=sorted(open_sites),
        assignments=assignments,
        objective_value=objective_value,
        metadata={
            "method": "repair_and_one_swap_local_search",
            "iterations": iterations,
            "initial_objective": initial_objective,
            "deadline_reached": deadline_reached,
            "site_safety": safety,
        },
    )

    validation = validate_solution(instance, solution)
    if not validation.feasible:
        raise ValueError(
            "La soluzione della local search non è ammissibile: "
            + "; ".join(validation.errors)
        )

    return solution


def solve_local_search(
    instance: ProblemInstance,
    max_iterations: int = 100,
    repair_node_limit: int = 100_000,
    deadline: float | None = None,
) -> Solution:
    """Migliora la greedy mediante riparazione e scambi uno-a-uno.

    La deadline è globale e opzionale. Se scade dopo che è stata
    costruita una soluzione ammissibile, la procedura restituisce la
    migliore soluzione corrente.
    """

    if max_iterations < 0:
        raise ValueError(
            "Il numero massimo di iterazioni non può essere negativo."
        )

    instance.validate()
    safety = compute_site_safety(instance)

    try:
        greedy_solution = solve_greedy(instance)
        current_sites = sorted(greedy_solution.open_sites)
        current_assignments = greedy_solution.assignments
    except ValueError:
        current_sites = sorted(
            _select_sites_with_capacity_lookahead(instance, safety)
        )
        repaired = find_feasible_assignment(
            instance,
            current_sites,
            node_limit=repair_node_limit,
            deadline=deadline,
        )
        if repaired is None:
            raise ValueError(
                "Impossibile riparare l'insieme iniziale di siti "
                "selezionato dalla greedy."
            )
        current_assignments = repaired

    initial_objective = min(
        safety[site_id] for site_id in current_sites
    )
    current_score = _site_set_score(current_sites, safety)
    all_site_ids = sorted(site.id for site in instance.sites)

    iterations = 0
    stopped_by_deadline = _deadline_reached(deadline)

    while (
        iterations < max_iterations
        and not stopped_by_deadline
    ):
        closed_sites = [
            site_id
            for site_id in all_site_ids
            if site_id not in current_sites
        ]

        best_neighbor_sites: list[str] | None = None
        best_neighbor_assignments: dict[str, str] | None = None
        best_neighbor_score = current_score

        for site_out, site_in in product(
            current_sites,
            closed_sites,
        ):
            if _deadline_reached(deadline):
                stopped_by_deadline = True
                break

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

            if candidate_score <= best_neighbor_score:
                continue

            try:
                assignments = find_feasible_assignment(
                    instance,
                    candidate_sites,
                    node_limit=repair_node_limit,
                    deadline=deadline,
                )
            except TimeoutError:
                stopped_by_deadline = True
                break

            if assignments is None:
                continue

            best_neighbor_sites = candidate_sites
            best_neighbor_assignments = assignments
            best_neighbor_score = candidate_score

        if (
            stopped_by_deadline
            or best_neighbor_sites is None
            or best_neighbor_assignments is None
        ):
            break

        current_sites = best_neighbor_sites
        current_assignments = best_neighbor_assignments
        current_score = best_neighbor_score
        iterations += 1

    return _build_solution(
        instance=instance,
        open_sites=current_sites,
        assignments=current_assignments,
        safety=safety,
        iterations=iterations,
        initial_objective=initial_objective,
        deadline_reached=stopped_by_deadline,
    )
