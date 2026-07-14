"""Test del generatore delle classi di istanze."""

from cmmoflp_nuclear_siting.generation.generator import (
    GenerationConfig,
    generate_instance,
)


def build_config(
    *,
    seed: int = 42,
    distribution: str = "uniform",
    capacity_level: str = "medium",
    capacity_factor: float | None = None,
) -> GenerationConfig:
    return GenerationConfig(
        name="generator_test",
        communities=30,
        candidate_sites=10,
        plants_to_open=3,
        seed=seed,
        distribution=distribution,
        capacity_level=capacity_level,
        capacity_factor=capacity_factor,
    )


def test_generation_is_reproducible() -> None:
    first = generate_instance(build_config(seed=123))
    second = generate_instance(build_config(seed=123))

    assert first.communities == second.communities
    assert first.sites == second.sites
    assert first.metadata == second.metadata


def test_different_seeds_generate_different_instances() -> None:
    first = generate_instance(build_config(seed=1))
    second = generate_instance(build_config(seed=2))

    assert first.communities != second.communities
    assert first.sites != second.sites


def test_uniform_and_clustered_instances_are_valid() -> None:
    uniform = generate_instance(
        build_config(distribution="uniform")
    )
    clustered = generate_instance(
        build_config(distribution="clustered")
    )

    uniform.validate()
    clustered.validate()

    assert uniform.metadata["distribution"] == "uniform"
    assert clustered.metadata["distribution"] == "clustered"


def test_generator_constructs_a_guaranteed_feasible_solution() -> None:
    instance = generate_instance(
        build_config(
            distribution="clustered",
            capacity_level="tight",
        )
    )

    selected_sites = instance.metadata["guaranteed_feasible_sites"]
    assignment = instance.metadata["guaranteed_assignment"]
    capacities = {site.id: site.capacity for site in instance.sites}
    demands = {
        community.id: community.demand
        for community in instance.communities
    }

    assert len(selected_sites) == instance.p
    assert set(assignment) == set(demands)
    assert set(assignment.values()).issubset(set(selected_sites))

    loads = {site_id: 0.0 for site_id in selected_sites}
    for community_id, site_id in assignment.items():
        loads[site_id] += demands[community_id]

    assert all(
        loads[site_id] <= capacities[site_id]
        for site_id in selected_sites
    )


def test_capacity_levels_control_available_capacity() -> None:
    tight = generate_instance(
        build_config(
            seed=777,
            capacity_level="tight",
            capacity_factor=1.05,
        )
    )
    medium = generate_instance(
        build_config(
            seed=777,
            capacity_level="medium",
            capacity_factor=1.20,
        )
    )
    loose = generate_instance(
        build_config(
            seed=777,
            capacity_level="loose",
            capacity_factor=1.50,
        )
    )

    def guaranteed_capacity(instance) -> float:
        selected = set(
            instance.metadata["guaranteed_feasible_sites"]
        )
        return sum(
            site.capacity
            for site in instance.sites
            if site.id in selected
        )

    assert guaranteed_capacity(tight) < guaranteed_capacity(medium)
    assert guaranteed_capacity(medium) < guaranteed_capacity(loose)
