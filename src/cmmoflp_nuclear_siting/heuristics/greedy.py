"""Euristica greedy di base per il CMMOFLP nucleare."""

from __future__ import annotations

from collections.abc import Iterable

from ..core.instance import ProblemInstance
from ..core.solution import Solution
from ..core.validation import validate_solution


def compute_site_safety(instance: ProblemInstance) -> dict[str, float]:
    """Calcola la distanza dalla comunità più vicina per ogni sito."""

    return {
        site.id: min(
            instance.distance(community.id, site.id)
            for community in instance.communities
        )
        for site in instance.sites
    }


def _select_sites_with_capacity_lookahead(
    instance: ProblemInstance,
    safety: dict[str, float],
) -> list[str]:
    """Seleziona p siti privilegiando sicurezza e fattibilità di capacità totale.

    A ogni passo viene scelto il sito più sicuro che consente ancora,
    utilizzando i posti rimanenti, di raggiungere almeno la domanda totale.
    """

    total_demand = sum(community.demand for community in instance.communities)
    capacity = {site.id: site.capacity for site in instance.sites}

    ordered_sites = sorted(
        (site.id for site in instance.sites),
        key=lambda site_id: (-safety[site_id], -capacity[site_id], site_id),
    )

    selected: list[str] = []

    while len(selected) < instance.p:
        chosen_site: str | None = None

        for candidate in ordered_sites:
            if candidate in selected:
                continue

            trial = selected + [candidate]
            slots_left = instance.p - len(trial)

            remaining_capacities = sorted(
                (
                    capacity[site_id]
                    for site_id in ordered_sites
                    if site_id not in trial
                ),
                reverse=True,
            )

            maximum_reachable_capacity = (
                sum(capacity[site_id] for site_id in trial)
                + sum(remaining_capacities[:slots_left])
            )

            if maximum_reachable_capacity + 1e-9 >= total_demand:
                chosen_site = candidate
                break

        if chosen_site is None:
            raise ValueError(
                "La greedy non riesce a selezionare p siti con capacità totale sufficiente."
            )

        selected.append(chosen_site)

    return selected


def _assign_communities_best_fit(
    instance: ProblemInstance,
    open_sites: Iterable[str],
    safety: dict[str, float],
) -> dict[str, str]:
    """Assegna le comunità con una strategia best-fit decrescente.

    Le comunità vengono ordinate per domanda decrescente. Ogni comunità
    viene assegnata alla centrale che, dopo l'assegnamento, lascia la
    minore capacità residua non negativa.
    """

    open_sites = list(open_sites)
    capacity = {site.id: site.capacity for site in instance.sites}
    remaining_capacity = {
        site_id: capacity[site_id]
        for site_id in open_sites
    }

    communities = sorted(
        instance.communities,
        key=lambda community: (-community.demand, community.id),
    )

    assignments: dict[str, str] = {}

    for community in communities:
        feasible_sites = [
            site_id
            for site_id in open_sites
            if remaining_capacity[site_id] + 1e-9 >= community.demand
        ]

        if not feasible_sites:
            raise ValueError(
                "La greedy non riesce a costruire un assegnamento capacitato ammissibile."
            )

        chosen_site = min(
            feasible_sites,
            key=lambda site_id: (
                remaining_capacity[site_id] - community.demand,
                -safety[site_id],
                site_id,
            ),
        )

        assignments[community.id] = chosen_site
        remaining_capacity[chosen_site] -= community.demand

    return assignments


def solve_greedy(instance: ProblemInstance) -> Solution:
    """Costruisce una soluzione greedy ammissibile per il CMMOFLP."""

    instance.validate()
    safety = compute_site_safety(instance)

    open_sites = _select_sites_with_capacity_lookahead(instance, safety)
    assignments = _assign_communities_best_fit(instance, open_sites, safety)

    objective_value = min(safety[site_id] for site_id in open_sites)

    solution = Solution(
        open_sites=open_sites,
        assignments=assignments,
        objective_value=objective_value,
        metadata={
            "method": "capacity_aware_greedy",
            "site_safety": safety,
        },
    )

    validation = validate_solution(instance, solution)
    if not validation.feasible:
        raise ValueError(
            "La soluzione greedy non ha superato la validazione: "
            + "; ".join(validation.errors)
        )

    return solution
