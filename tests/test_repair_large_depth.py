"""Test del repair su istanze oltre il limite ricorsivo standard."""

from cmmoflp_nuclear_siting.core.instance import (
    CandidateSite,
    Community,
    ProblemInstance,
)
from cmmoflp_nuclear_siting.heuristics.repair import (
    find_feasible_assignment,
)


def test_repair_handles_more_than_one_thousand_communities() -> None:
    communities = [
        Community(
            id=f"c{index}",
            x=0.0,
            y=0.0,
            demand=1.0,
        )
        for index in range(1200)
    ]
    instance = ProblemInstance(
        name="deep_repair",
        p=1,
        communities=communities,
        sites=[
            CandidateSite(
                id="s1",
                x=10.0,
                y=0.0,
                capacity=1200.0,
            )
        ],
    )

    assignment = find_feasible_assignment(
        instance,
        open_sites=["s1"],
        node_limit=2_000,
    )

    assert assignment is not None
    assert len(assignment) == 1200
    assert set(assignment.values()) == {"s1"}
