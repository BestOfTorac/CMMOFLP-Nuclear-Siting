"""Ricerca locale con riparazione per il CMMOFLP nucleare."""

from __future__ import annotations

from itertools import product

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
    """Restituisce il punteggio lessicografico di un insieme di siti.

    Il primo valore è l'obiettivo maximin.
    Il secondo valore, usato soltanto come spareggio, è la somma
    dei valori di sicurezza dei siti aperti.
    """

    return (
        min(safety[site_id] for site_id in open_sites),
        sum(safety[site_id] for site_id in open_sites),
    )


def _build_solution(
    instance: ProblemInstance,
    open_sites: list[str],
    assignments: dict[str, str],
    safety: dict[str, float],
    iterations: int,
    initial_objective: float,
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
) -> Solution:
    """Migliora la greedy mediante riparazione e scambi uno-a-uno.

    Procedura:
    1. costruisce la selezione iniziale della greedy;
    2. ripara l'assegnamento con backtracking quando il best-fit fallisce;
    3. valuta tutti gli scambi tra un sito aperto e uno chiuso;
    4. accetta il miglior vicino ammissibile con punteggio superiore;
    5. termina quando non esiste più uno scambio migliorativo.
    """

    if max_iterations < 0:
        raise ValueError("Il numero massimo di iterazioni non può essere negativo.")

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
        )
        if repaired is None:
            raise ValueError(
                "Impossibile riparare l'insieme iniziale di siti selezionato dalla greedy."
            )
        current_assignments = repaired

    initial_objective = min(safety[site_id] for site_id in current_sites)
    current_score = _site_set_score(current_sites, safety)
    all_site_ids = sorted(site.id for site in instance.sites)

    iterations = 0

    while iterations < max_iterations:
        closed_sites = [
            site_id
            for site_id in all_site_ids
            if site_id not in current_sites
        ]

        best_neighbor_sites: list[str] | None = None
        best_neighbor_assignments: dict[str, str] | None = None
        best_neighbor_score = current_score

        for site_out, site_in in product(current_sites, closed_sites):
            candidate_sites = sorted(
                [
                    site_id
                    for site_id in current_sites
                    if site_id != site_out
                ]
                + [site_in]
            )
            candidate_score = _site_set_score(candidate_sites, safety)

            if candidate_score <= best_neighbor_score:
                continue

            assignments = find_feasible_assignment(
                instance,
                candidate_sites,
                node_limit=repair_node_limit,
            )
            if assignments is None:
                continue

            best_neighbor_sites = candidate_sites
            best_neighbor_assignments = assignments
            best_neighbor_score = candidate_score

        if best_neighbor_sites is None or best_neighbor_assignments is None:
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
    )
