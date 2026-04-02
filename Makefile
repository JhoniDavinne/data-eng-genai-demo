.PHONY: lint test package install clean run

install:
	pip install -e ".[dev]"

lint:
	black --check src/ tests/
	flake8 src/ tests/ --max-line-length 88 --extend-ignore E203,W503

format:
	black src/ tests/

test:
	pytest -v

package:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

run:
	python -m src.main
