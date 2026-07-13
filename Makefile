.PHONY: install test check-toy

install:
	python -m pip install -r requirements-dev.txt

test:
	pytest

check-toy:
	python scripts/check_instance.py instances/test/toy_instance_01.json
