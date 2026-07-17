.PHONY: install test analysis check check-toy

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -W error::FutureWarning

analysis:
	python scripts/analyze_final_results.py
	python scripts/analyze_ablation.py

check: test analysis

check-toy:
	python scripts/check_instance.py instances/test/toy_instance_01.json
