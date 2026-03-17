PYTHON_VERSION ?= 3.11

.PHONY: bootstrap doctor test scan lint format

bootstrap:
	uv python install $(PYTHON_VERSION)
	uv sync --python $(PYTHON_VERSION) --extra dev
	./scripts/bootstrap_aihubshell.sh

doctor:
	uv sync --python $(PYTHON_VERSION) --extra dev
	./scripts/doctor.sh

test:
	uv sync --python $(PYTHON_VERSION) --extra dev
	uv run pytest

scan:
	uv sync --python $(PYTHON_VERSION) --extra dev
	./scripts/run_scan.sh

lint:
	uv sync --python $(PYTHON_VERSION) --extra dev
	uv run ruff check .

format:
	uv sync --python $(PYTHON_VERSION) --extra dev
	uv run ruff format .

