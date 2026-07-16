"""Unisce più manifest di istanze in un unico file CSV."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cmmoflp_nuclear_siting.analysis.manifest_merge import (  # noqa: E402
    merge_manifests,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Unisce più manifest CSV di istanze."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help="Manifest da unire.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Manifest CSV risultante.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    rows = merge_manifests(args.inputs, args.output)

    print("\n=== MERGE MANIFEST ===")
    print(f"Manifest uniti: {len(args.inputs)}")
    print(f"Istanze complessive: {len(rows)}")
    print(f"Output: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
