.PHONY: help install install-dev test test-cov lint format mypy bandit clean build publish

help:
	@echo "Available commands:"
	@echo "  install      - Install package"
	@echo "  install-dev  - Install package with development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run pylint"
	@echo "  format       - Format code with black"
	@echo "  mypy         - Run type checking"
	@echo "  bandit       - Run security check"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  publish      - Publish to PyPI (requires credentials)"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-cov:
	pytest --cov=remote_hosts --cov-report=html --cov-report=term

lint:
	pylint remote_hosts/

format:
	black remote_hosts/ tests/

mypy:
	mypy remote_hosts/

bandit:
	bandit -r remote_hosts/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -f .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish: build
	twine check dist/*
	twine upload dist/*
