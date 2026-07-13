"""Generatore iniziale di istanze riproducibili."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random

from ..core.instance import CandidateSite, Community, ProblemInstance


@dataclass(frozen=True)
class GenerationConfig:
    """Parametri minimi per una istanza uniforme."""

    name: str
    communities: int
    candidate_sites: int
    plants_to_open: int
    capacity_factor: float
    seed: int
    coordinate_limit: float = 100.0


def generate_uniform_instance(config: GenerationConfig) -> ProblemInstance:
    """Genera una istanza uniforme con capacità potenzialmente sufficiente."""

    if config.communities <= 0:
        raise ValueError("Il numero di comunità deve essere positivo.")
    if config.candidate_sites < config.plants_to_open:
        raise ValueError("I siti candidati devono essere almeno pari alle centrali.")
    if config.capacity_factor < 1.0:
        raise ValueError("Il fattore di capacità deve essere almeno 1.")

    rng = random.Random(config.seed)

    communities = [
        Community(
            id=f"c{index + 1}",
            x=rng.uniform(0, config.coordinate_limit),
            y=rng.uniform(0, config.coordinate_limit),
            demand=float(rng.randint(5, 20)),
        )
        for index in range(config.communities)
    ]

    total_demand = sum(item.demand for item in communities)
    base_capacity = math.ceil(
        total_demand * config.capacity_factor / config.plants_to_open
    )

    sites = [
        CandidateSite(
            id=f"s{index + 1}",
            x=rng.uniform(0, config.coordinate_limit),
            y=rng.uniform(0, config.coordinate_limit),
            capacity=float(max(1, round(base_capacity * rng.uniform(0.9, 1.1)))),
        )
        for index in range(config.candidate_sites)
    ]

    best_p = sorted(sites, key=lambda item: item.capacity, reverse=True)[
        : config.plants_to_open
    ]
    deficit = total_demand - sum(item.capacity for item in best_p)

    if deficit > 0:
        largest = max(sites, key=lambda item: item.capacity)
        sites = [
            CandidateSite(
                id=item.id,
                x=item.x,
                y=item.y,
                capacity=item.capacity + math.ceil(deficit)
                if item.id == largest.id
                else item.capacity,
            )
            for item in sites
        ]

    instance = ProblemInstance(
        name=config.name,
        p=config.plants_to_open,
        communities=communities,
        sites=sites,
        metadata={
            "distribution": "uniform",
            "capacity_factor": config.capacity_factor,
            "seed": config.seed,
        },
    )
    instance.validate()
    return instance
