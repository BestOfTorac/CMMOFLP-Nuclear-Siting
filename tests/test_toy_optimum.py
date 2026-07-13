"""Verifica indipendente dell'ottimo della toy instance mediante enumerazione completa."""

from itertools import combinations, product
from pathlib import Path

import pytest

from cmmoflp_nuclear_siting.core.instance import ProblemInstance


TOY_PATH = Path("instances/test/toy_instance_01.json")


def has_feasible_assignment(
    instance: ProblemInstance,
    open_sites: tuple[str, ...],
) -> bool:
    """Restituisce True se esiste un assegnamento che rispetta le capacità."""

    demand = {community.id: community.demand for community in instance.communities}
    capacity = {site.id: site.capacity for site in instance.sites}
    community_ids = [community.id for community in instance.communities]

    for assigned_sites in product(open_sites, repeat=len(community_ids)):
        loads = {site_id: 0.0 for site_id in open_sites}

        for community_id, site_id in zip(community_ids, assigned_sites):
            loads[site_id] += demand[community_id]

        if all(loads[site_id] <= capacity[site_id] for site_id in open_sites):
            return True

    return False


def objective_value(
    instance: ProblemInstance,
    open_sites: tuple[str, ...],
) -> float:
    """Calcola la minima distanza comunità-centrale aperta."""

    return min(
        instance.distance(community.id, site_id)
        for community in instance.communities
        for site_id in open_sites
    )


def test_toy_instance_optimum_by_complete_enumeration() -> None:
    """Verifica siti ottimi e valore obiettivo della toy instance."""

    instance = ProblemInstance.from_json(TOY_PATH)
    site_ids = [site.id for site in instance.sites]

    feasible_solutions: list[tuple[float, tuple[str, ...]]] = []

    for open_sites in combinations(site_ids, instance.p):
        if has_feasible_assignment(instance, open_sites):
            feasible_solutions.append(
                (objective_value(instance, open_sites), open_sites)
            )

    best_value, best_sites = max(feasible_solutions)

    assert best_sites == ("s1", "s4")
    assert best_value == pytest.approx(18.0277563773, abs=1e-6)
