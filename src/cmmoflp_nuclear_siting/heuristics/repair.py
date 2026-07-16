"""Procedure di riparazione degli assegnamenti per il CMMOFLP."""

from __future__ import annotations

from collections.abc import Iterable
from time import perf_counter

from ..core.instance import ProblemInstance


def _check_deadline(deadline: float | None) -> None:
    """Interrompe la ricerca quando il limite temporale è scaduto."""

    if deadline is not None and perf_counter() >= deadline:
        raise TimeoutError(
            "Il limite temporale della riparazione è stato raggiunto."
        )


def find_feasible_assignment(
    instance: ProblemInstance,
    open_sites: Iterable[str],
    node_limit: int = 100_000,
    deadline: float | None = None,
) -> dict[str, str] | None:
    """Cerca un assegnamento capacitato per un insieme fissato di siti.

    La procedura utilizza un backtracking deterministico con:
    - comunità ordinate per domanda decrescente;
    - scelta best-fit dei siti;
    - eliminazione delle simmetrie tra capacità residue uguali;
    - memoizzazione degli stati non ammissibili;
    - limite massimo al numero di nodi esplorati;
    - deadline globale opzionale.

    Restituisce un dizionario comunità-sito oppure ``None``.
    Solleva ``TimeoutError`` se la deadline scade durante la ricerca.
    """

    if node_limit <= 0:
        raise ValueError("Il limite di nodi deve essere positivo.")

    _check_deadline(deadline)
    instance.validate()

    selected_sites = tuple(dict.fromkeys(open_sites))
    known_sites = {site.id for site in instance.sites}

    if not selected_sites:
        return None
    if not set(selected_sites).issubset(known_sites):
        raise ValueError(
            "La procedura di riparazione ha ricevuto siti sconosciuti."
        )

    capacity = {site.id: site.capacity for site in instance.sites}
    total_demand = sum(
        community.demand for community in instance.communities
    )

    if (
        sum(capacity[site_id] for site_id in selected_sites)
        + 1e-9
        < total_demand
    ):
        return None

    communities = sorted(
        instance.communities,
        key=lambda community: (-community.demand, community.id),
    )

    if max(community.demand for community in communities) > (
        max(capacity[site_id] for site_id in selected_sites) + 1e-9
    ):
        return None

    site_order = tuple(
        sorted(
            selected_sites,
            key=lambda site_id: (-capacity[site_id], site_id),
        )
    )
    remaining = {
        site_id: capacity[site_id]
        for site_id in site_order
    }

    assignment: dict[str, str] = {}
    failed_states: set[tuple[int, tuple[float, ...]]] = set()
    explored_nodes = 0

    def search(index: int) -> bool:
        nonlocal explored_nodes

        _check_deadline(deadline)

        if index == len(communities):
            return True

        if explored_nodes >= node_limit:
            return False

        state = (
            index,
            tuple(
                round(remaining[site_id], 8)
                for site_id in site_order
            ),
        )
        if state in failed_states:
            return False

        explored_nodes += 1
        community = communities[index]

        candidates = [
            site_id
            for site_id in site_order
            if remaining[site_id] + 1e-9 >= community.demand
        ]
        candidates.sort(
            key=lambda site_id: (
                remaining[site_id] - community.demand,
                site_id,
            )
        )

        tried_residual_capacities: set[float] = set()

        for site_id in candidates:
            _check_deadline(deadline)

            residual_key = round(remaining[site_id], 8)
            if residual_key in tried_residual_capacities:
                continue
            tried_residual_capacities.add(residual_key)

            remaining[site_id] -= community.demand
            assignment[community.id] = site_id

            if search(index + 1):
                return True

            remaining[site_id] += community.demand
            assignment.pop(community.id, None)

        failed_states.add(state)
        return False

    if search(0):
        return assignment.copy()

    return None
