PYTHON ?= python3
.PHONY: run test lint format build build-pypi build-deb verify
run:
	./gunterdown

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) -m compileall -q src tests scripts
	$(PYTHON) scripts/check.py

format:
	$(PYTHON) -m black src tests scripts
	$(PYTHON) -m isort src tests scripts

build build-pypi:
	$(PYTHON) scripts/build.py

build-deb:
	./scripts/build-deb.sh

verify: lint test build
