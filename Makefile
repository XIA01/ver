# Makefile para Proyecto GAZE-INFERENCE
# Tasks comunes para desarrollo

.PHONY: help install install-dev clean test lint format run-app run-tests benchmark

help:
	@echo "Comandos disponibles:"
	@echo "  make install        - Instalar dependencias de producción"
	@echo "  make install-dev    - Instalar dependencias de desarrollo"
	@echo "  make clean          - Limpiar archivos temporales"
	@echo "  make test           - Correr tests con cobertura"
	@echo "  make lint           - Verificar código (pylint)"
	@echo "  make format         - Formatear código (black)"
	@echo "  make run-app        - Ejecutar aplicación principal"
	@echo "  make benchmark      - Correr benchmarks de latencia"
	@echo "  make ci             - Simular CI localmente (test + lint)"

install:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

install-dev:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/ dist/ build/ *.egg-info 2>/dev/null || true

test:
	pytest --cov=src --cov-report=html --cov-report=term -v

test-fast:
	pytest -m "not slow" -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-latency:
	pytest tests/test_latency.py -v

lint:
	pylint src/ --fail-under=8.0

lint-check:
	black --check src/
	pylint src/

format:
	black src/
	isort src/  # Organizar imports

run-app:
	python scripts/run.py

run-calibrate:
	python scripts/calibrate.py

benchmark:
	pytest tests/test_latency.py::TestLatency -v --benchmark-only

profile:
	python -m cProfile -s cumtime scripts/run.py > profile.txt
	head -30 profile.txt

ci: clean lint test
	@echo "✅ CI checks passed!"

setup-git-hooks:
	@echo "Installing pre-commit hooks..."
	pip install pre-commit
	pre-commit install
	@echo "✅ Git hooks installed"

validate-latency:
	python scripts/validate_latency.py

.PHONY: help install install-dev clean test test-fast test-unit test-integration test-latency lint lint-check format run-app run-calibrate benchmark profile ci setup-git-hooks validate-latency
