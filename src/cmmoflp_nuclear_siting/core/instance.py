"""Definizione e validazione delle istanze del problema."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Community:
    """Comunità con coordinate e domanda energetica."""

    id: str
    x: float
    y: float
    demand: float


@dataclass(frozen=True)
class CandidateSite:
    """Sito candidato con coordinate e capacità produttiva."""

    id: str
    x: float
    y: float
    capacity: float


@dataclass
class ProblemInstance:
    """Istanza completa del CMMOFLP."""

    name: str
    p: int
    communities: list[Community]
    sites: list[CandidateSite]
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Solleva ValueError quando l'istanza non supera i controlli di base."""

        if not self.name.strip():
            raise ValueError("Il nome dell'istanza non può essere vuoto.")
        if self.p <= 0:
            raise ValueError("Il numero di centrali p deve essere positivo.")
        if not self.communities:
            raise ValueError("L'istanza deve contenere almeno una comunità.")
        if len(self.sites) < self.p:
            raise ValueError("Il numero di siti candidati deve essere almeno pari a p.")

        community_ids = [item.id for item in self.communities]
        site_ids = [item.id for item in self.sites]

        if len(community_ids) != len(set(community_ids)):
            raise ValueError("Gli identificativi delle comunità devono essere univoci.")
        if len(site_ids) != len(set(site_ids)):
            raise ValueError("Gli identificativi dei siti devono essere univoci.")

        for community in self.communities:
            if community.demand <= 0:
                raise ValueError(f"Domanda non positiva per la comunità {community.id}.")
            if not all(math.isfinite(v) for v in (community.x, community.y, community.demand)):
                raise ValueError(f"Valori non finiti per la comunità {community.id}.")

        for site in self.sites:
            if site.capacity <= 0:
                raise ValueError(f"Capacità non positiva per il sito {site.id}.")
            if not all(math.isfinite(v) for v in (site.x, site.y, site.capacity)):
                raise ValueError(f"Valori non finiti per il sito {site.id}.")

        total_demand = sum(item.demand for item in self.communities)
        best_p_capacity = sum(
            sorted((item.capacity for item in self.sites), reverse=True)[: self.p]
        )
        if best_p_capacity + 1e-9 < total_demand:
            raise ValueError(
                "Neppure i p siti con capacità maggiore possono soddisfare la domanda totale."
            )

    def distance(self, community_id: str, site_id: str) -> float:
        """Restituisce la distanza euclidea tra una comunità e un sito."""

        community = next((x for x in self.communities if x.id == community_id), None)
        site = next((x for x in self.sites if x.id == site_id), None)

        if community is None:
            raise KeyError(f"Comunità sconosciuta: {community_id}")
        if site is None:
            raise KeyError(f"Sito sconosciuto: {site_id}")

        return math.hypot(community.x - site.x, community.y - site.y)

    def distance_matrix(self) -> dict[str, dict[str, float]]:
        """Calcola la matrice delle distanze comunità-sito."""

        return {
            community.id: {
                site.id: self.distance(community.id, site.id) for site in self.sites
            }
            for community in self.communities
        }

    @classmethod
    def from_json(cls, path: str | Path) -> "ProblemInstance":
        """Carica e valida un'istanza da un file JSON."""

        with Path(path).open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        instance = cls(
            name=str(data["name"]),
            p=int(data["p"]),
            communities=[
                Community(
                    id=str(item["id"]),
                    x=float(item["x"]),
                    y=float(item["y"]),
                    demand=float(item["demand"]),
                )
                for item in data["communities"]
            ],
            sites=[
                CandidateSite(
                    id=str(item["id"]),
                    x=float(item["x"]),
                    y=float(item["y"]),
                    capacity=float(item["capacity"]),
                )
                for item in data["sites"]
            ],
            metadata=dict(data.get("metadata", {})),
        )
        instance.validate()
        return instance

    def to_json(self, path: str | Path) -> None:
        """Salva l'istanza in formato JSON."""

        self.validate()
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "name": self.name,
            "p": self.p,
            "communities": [
                {"id": x.id, "x": x.x, "y": x.y, "demand": x.demand}
                for x in self.communities
            ],
            "sites": [
                {"id": x.id, "x": x.x, "y": x.y, "capacity": x.capacity}
                for x in self.sites
            ],
            "metadata": self.metadata,
        }

        with output.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
