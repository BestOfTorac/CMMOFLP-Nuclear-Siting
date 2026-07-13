"""Rappresentazione di una soluzione candidata."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Solution:
    """Soluzione con siti aperti, assegnamenti e metadati."""

    open_sites: list[str]
    assignments: dict[str, str]
    objective_value: float | None = None
    metadata: dict[str, object] = field(default_factory=dict)
