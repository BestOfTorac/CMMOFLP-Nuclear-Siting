"""Validazione delle soluzioni candidate."""

from __future__ import annotations

from dataclasses import dataclass

from .instance import ProblemInstance
from .solution import Solution


@dataclass(frozen=True)
class ValidationResult:
    """Esito della validazione."""

    feasible: bool
    objective_value: float | None
    errors: tuple[str, ...]


def validate_solution(
    instance: ProblemInstance,
    solution: Solution,
    tolerance: float = 1e-9,
) -> ValidationResult:
    """Controlla apertura, assegnamenti, capacità e valore maximin."""

    errors: list[str] = []
    open_sites = set(solution.open_sites)
    known_sites = {site.id for site in instance.sites}
    known_communities = {community.id for community in instance.communities}

    if len(solution.open_sites) != len(open_sites):
        errors.append("La lista dei siti aperti contiene duplicati.")
    if len(open_sites) != instance.p:
        errors.append(f"Devono essere aperti esattamente {instance.p} siti.")
    if not open_sites.issubset(known_sites):
        errors.append("La soluzione contiene siti sconosciuti.")

    assigned = set(solution.assignments)
    missing = known_communities - assigned
    extra = assigned - known_communities

    if missing:
        errors.append(f"Comunità non assegnate: {sorted(missing)}")
    if extra:
        errors.append(f"Assegnamenti per comunità sconosciute: {sorted(extra)}")

    loads = {site_id: 0.0 for site_id in open_sites}
    demand = {community.id: community.demand for community in instance.communities}

    for community_id, site_id in solution.assignments.items():
        if community_id not in known_communities:
            continue
        if site_id not in open_sites:
            errors.append(
                f"La comunità {community_id} è assegnata al sito non aperto {site_id}."
            )
            continue
        loads[site_id] += demand[community_id]

    capacities = {site.id: site.capacity for site in instance.sites}
    for site_id, load in loads.items():
        if load > capacities[site_id] + tolerance:
            errors.append(
                f"Capacità superata nel sito {site_id}: "
                f"carico {load}, capacità {capacities[site_id]}."
            )

    objective_value = None
    if open_sites and open_sites.issubset(known_sites):
        objective_value = min(
            instance.distance(community.id, site_id)
            for community in instance.communities
            for site_id in open_sites
        )

        if (
            solution.objective_value is not None
            and abs(solution.objective_value - objective_value) > tolerance
        ):
            errors.append(
                "Il valore obiettivo dichiarato non coincide con la distanza minima reale."
            )

    return ValidationResult(
        feasible=not errors,
        objective_value=objective_value,
        errors=tuple(errors),
    )
