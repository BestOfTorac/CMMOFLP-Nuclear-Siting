"""Genera una istanza uniforme di esempio."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.generation.generator import (  # noqa: E402
    GenerationConfig,
    generate_uniform_instance,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera una istanza uniforme.")
    parser.add_argument("--name", default="sample_uniform")
    parser.add_argument("--communities", type=int, default=30)
    parser.add_argument("--sites", type=int, default=10)
    parser.add_argument("--p", type=int, default=2)
    parser.add_argument("--capacity-factor", type=float, default=1.20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "instances/generated/sample_uniform.json",
    )
    args = parser.parse_args()

    config = GenerationConfig(
        name=args.name,
        communities=args.communities,
        candidate_sites=args.sites,
        plants_to_open=args.p,
        capacity_factor=args.capacity_factor,
        seed=args.seed,
    )
    instance = generate_uniform_instance(config)
    instance.to_json(args.output)
    print(f"Istanza salvata in: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
