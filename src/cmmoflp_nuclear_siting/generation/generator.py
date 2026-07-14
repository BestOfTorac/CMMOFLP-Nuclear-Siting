"""Generazione riproducibile delle classi di istanze del CMMOFLP."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
import random

from ..core.instance import CandidateSite, Community, ProblemInstance


CAPACITY_FACTORS: dict[str, float] = {
    "tight": 1.05,
    "medium": 1.20,
    "loose": 1.50,
}


@dataclass(frozen=True)
class GenerationConfig:
    """Configurazione di una singola istanza."""

    name: str
    communities: int
    candidate_sites: int
    plants_to_open: int
    seed: int
    distribution: str = "uniform"
    capacity_level: str = "medium"
    capacity_factor: float | None = None
    coordinate_limit: float = 100.0
    clusters: int = 3
    cluster_std_ratio: float = 0.08


def _resolve_capacity_factor(config: GenerationConfig) -> float:
    if config.capacity_factor is not None:
        return float(config.capacity_factor)

    try:
        return CAPACITY_FACTORS[config.capacity_level]
    except KeyError as exc:
        levels = ", ".join(sorted(CAPACITY_FACTORS))
        raise ValueError(
            f"Livello di capacità sconosciuto: {config.capacity_level}. "
            f"Valori ammessi: {levels}."
        ) from exc


def _validate_config(config: GenerationConfig) -> None:
    if config.communities <= 0:
        raise ValueError("Il numero di comunità deve essere positivo.")
    if config.candidate_sites <= 0:
        raise ValueError("Il numero di siti candidati deve essere positivo.")
    if config.plants_to_open <= 0:
        raise ValueError("Il numero di centrali da aprire deve essere positivo.")
    if config.candidate_sites < config.plants_to_open:
        raise ValueError("I siti candidati devono essere almeno pari alle centrali.")
    if config.coordinate_limit <= 0:
        raise ValueError("Il limite delle coordinate deve essere positivo.")
    if config.distribution not in {"uniform", "clustered"}:
        raise ValueError(
            "La distribuzione deve essere 'uniform' oppure 'clustered'."
        )
    if config.clusters <= 0:
        raise ValueError("Il numero di cluster deve essere positivo.")
    if config.cluster_std_ratio <= 0:
        raise ValueError("La deviazione dei cluster deve essere positiva.")
    if _resolve_capacity_factor(config) < 1.0:
        raise ValueError("Il fattore di capacità deve essere almeno 1.")


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _generate_community_coordinates(
    config: GenerationConfig,
    rng: random.Random,
) -> list[tuple[float, float]]:
    if config.distribution == "uniform":
        return [
            (
                rng.uniform(0.0, config.coordinate_limit),
                rng.uniform(0.0, config.coordinate_limit),
            )
            for _ in range(config.communities)
        ]

    cluster_count = min(config.clusters, config.communities)
    margin = 0.15 * config.coordinate_limit
    upper = config.coordinate_limit - margin

    centers = [
        (
            rng.uniform(margin, upper),
            rng.uniform(margin, upper),
        )
        for _ in range(cluster_count)
    ]

    standard_deviation = config.cluster_std_ratio * config.coordinate_limit
    coordinates: list[tuple[float, float]] = []

    for index in range(config.communities):
        center_x, center_y = centers[index % cluster_count]
        coordinates.append(
            (
                _clamp(
                    rng.gauss(center_x, standard_deviation),
                    0.0,
                    config.coordinate_limit,
                ),
                _clamp(
                    rng.gauss(center_y, standard_deviation),
                    0.0,
                    config.coordinate_limit,
                ),
            )
        )

    rng.shuffle(coordinates)
    return coordinates


def _build_guaranteed_partition(
    communities: list[Community],
    anchor_site_ids: list[str],
) -> tuple[dict[str, str], dict[str, float]]:
    """Costruisce un assegnamento LPT che garantisce la fattibilità."""

    loads = {site_id: 0.0 for site_id in anchor_site_ids}
    assignment: dict[str, str] = {}

    for community in sorted(
        communities,
        key=lambda item: (-item.demand, item.id),
    ):
        site_id = min(
            anchor_site_ids,
            key=lambda candidate: (loads[candidate], candidate),
        )
        assignment[community.id] = site_id
        loads[site_id] += community.demand

    return assignment, loads


def generate_instance(config: GenerationConfig) -> ProblemInstance:
    """Genera una istanza valida e riproducibile."""

    _validate_config(config)
    factor = _resolve_capacity_factor(config)
    rng = random.Random(config.seed)

    community_coordinates = _generate_community_coordinates(config, rng)
    communities = [
        Community(
            id=f"c{index + 1}",
            x=x,
            y=y,
            demand=float(rng.randint(5, 20)),
        )
        for index, (x, y) in enumerate(community_coordinates)
    ]

    site_coordinates = [
        (
            rng.uniform(0.0, config.coordinate_limit),
            rng.uniform(0.0, config.coordinate_limit),
        )
        for _ in range(config.candidate_sites)
    ]
    site_ids = [f"s{index + 1}" for index in range(config.candidate_sites)]

    anchor_site_ids = sorted(
        rng.sample(site_ids, config.plants_to_open)
    )
    guaranteed_assignment, guaranteed_loads = _build_guaranteed_partition(
        communities,
        anchor_site_ids,
    )

    total_demand = sum(community.demand for community in communities)
    average_capacity = total_demand * factor / config.plants_to_open

    capacities: dict[str, float] = {}
    for site_id in site_ids:
        if site_id in guaranteed_loads:
            capacities[site_id] = float(
                max(1, math.ceil(guaranteed_loads[site_id] * factor))
            )
        else:
            capacities[site_id] = float(
                max(
                    1,
                    round(average_capacity * rng.uniform(0.70, 1.15)),
                )
            )

    sites = [
        CandidateSite(
            id=site_id,
            x=site_coordinates[index][0],
            y=site_coordinates[index][1],
            capacity=capacities[site_id],
        )
        for index, site_id in enumerate(site_ids)
    ]

    class_id = (
        f"{config.communities}c_"
        f"{config.candidate_sites}s_"
        f"p{config.plants_to_open}_"
        f"{config.distribution}_"
        f"{config.capacity_level}"
    )

    instance = ProblemInstance(
        name=config.name,
        p=config.plants_to_open,
        communities=communities,
        sites=sites,
        metadata={
            "class_id": class_id,
            "distribution": config.distribution,
            "capacity_level": config.capacity_level,
            "capacity_factor": factor,
            "seed": config.seed,
            "coordinate_limit": config.coordinate_limit,
            "clusters": (
                config.clusters
                if config.distribution == "clustered"
                else None
            ),
            "guaranteed_feasible_sites": anchor_site_ids,
            "guaranteed_assignment": guaranteed_assignment,
            "guaranteed_loads": guaranteed_loads,
        },
    )
    instance.validate()
    return instance


def generate_uniform_instance(config: GenerationConfig) -> ProblemInstance:
    """Wrapper compatibile con gli script iniziali."""

    return generate_instance(replace(config, distribution="uniform"))
