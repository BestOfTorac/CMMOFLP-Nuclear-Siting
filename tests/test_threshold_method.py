"""Verifica indipendente del metodo esatto a soglia sulla toy instance."""

from itertools import combinations, product
from pathlib import Path

import pytest

from cmmoflp_nuclear_siting.core.instance import ProblemInstance


TOY_PATH = Path("instances/test/toy_instance_01.json")


def site_safety_values(instance: ProblemInstance) -> dict[str, float]:
    """Calcola la distanza dalla comunità più vicina per ogni sito."""

    return {
        site.id: min(
            instance.distance(community.id, site.id)
            for community in instance.communities
        )
        for site in instance.sites
    }


def has_feasible_assignment(
    instance: ProblemInstance,
    open_sites: tuple[str, ...],
) -> bool:
    """Verifica per enumerazione se esiste un assegnamento capacitato."""

    community_ids = [community.id for community in instance.communities]
    demand = {community.id: community.demand for community in instance.communities}
    capacity = {site.id: site.capacity for site in instance.sites}

    for assigned_sites in product(open_sites, repeat=len(community_ids)):
        loads = {site_id: 0.0 for site_id in open_sites}

        for community_id, site_id in zip(community_ids, assigned_sites):
            loads[site_id] += demand[community_id]

        if all(loads[site_id] <= capacity[site_id] for site_id in open_sites):
            return True

    return False


def is_threshold_feasible(
    instance: ProblemInstance,
    threshold: float,
    tolerance: float = 1e-9,
) -> tuple[bool, tuple[str, ...] | None]:
    """Verifica se esiste una scelta di p siti compatibile con la soglia."""

    safety = site_safety_values(instance)
    eligible_sites = [
        site.id
        for site in instance.sites
        if safety[site.id] + tolerance >= threshold
    ]

    for open_sites in combinations(eligible_sites, instance.p):
        if has_feasible_assignment(instance, open_sites):
            return True, open_sites

    return False, None


def test_threshold_candidate_levels_are_correct() -> None:
    """Controlla i livelli distinti generati dalla toy instance."""

    instance = ProblemInstance.from_json(TOY_PATH)
    safety = site_safety_values(instance)

    thresholds = sorted(set(safety.values()), reverse=True)

    assert thresholds == pytest.approx(
        [33.5410196625, 18.0277563773, 15.8113883008],
        abs=1e-6,
    )


def test_high_threshold_is_infeasible() -> None:
    """La soglia più alta consente un solo sito e deve essere infeasible."""

    instance = ProblemInstance.from_json(TOY_PATH)

    feasible, open_sites = is_threshold_feasible(instance, 33.5410196625)

    assert not feasible
    assert open_sites is None


def test_optimal_threshold_is_feasible() -> None:
    """La soglia ottima deve selezionare s1 e s4."""

    instance = ProblemInstance.from_json(TOY_PATH)

    feasible, open_sites = is_threshold_feasible(instance, 18.0277563773)

    assert feasible
    assert open_sites == ("s1", "s4")


def test_best_feasible_threshold_matches_compact_optimum() -> None:
    """La migliore soglia ammissibile deve coincidere con l'ottimo compatto."""

    instance = ProblemInstance.from_json(TOY_PATH)
    safety = site_safety_values(instance)

    best_threshold = None
    best_sites = None

    for threshold in sorted(set(safety.values()), reverse=True):
        feasible, open_sites = is_threshold_feasible(instance, threshold)
        if feasible:
            best_threshold = threshold
            best_sites = open_sites
            break

    assert best_threshold == pytest.approx(18.0277563773, abs=1e-6)
    assert best_sites == ("s1", "s4")
