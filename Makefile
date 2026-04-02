.PHONY: lint test package install clean

install:
	pip install -e ".[dev]"

lint:
	black --check src/ tests/
	flake8 src/ tests/

format:
	black src/ tests/

test:
	pytest tests/ -v

package:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
