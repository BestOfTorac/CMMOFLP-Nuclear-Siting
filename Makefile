.PHONY: install test analysis plots check check-toy

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -W error::FutureWarning

analysis:
	python scripts/analyze_final_results.py
	python scripts/analyze_ablation.py

plots:
	python scripts/generate_final_plots.py

check: test analysis plots

check-toy:
	python scripts/check_instance.py instances/test/toy_instance_01.json
