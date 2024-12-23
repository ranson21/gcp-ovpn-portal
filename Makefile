.PHONY: install run test lint format clean build publish-test publish dev-setup

# Poetry as the package manager
POETRY = poetry

# Install dependencies
install:
	$(POETRY) install

# Run development server
run:
	$(POETRY) run ovpn-portal

# Run tests
test:
	$(POETRY) run pytest tests/ -v

# Run tests with coverage
coverage:
	$(POETRY) run pytest --cov=ovpn_portal --cov-report=term-missing --cov-report=html --cov-report=xml:coverage.xml tests/
	@echo "Coverage report generated in coverage_html/index.html"

# Run linting
lint:
	$(POETRY) run flake8 ovpn_portal/ tests/
	$(POETRY) run black --check ovpn_portal/ tests/
	$(POETRY) run isort --check-only ovpn_portal/ tests/

# Format code
format:
	$(POETRY) run black ovpn_portal/ tests/
	$(POETRY) run isort ovpn_portal/ tests/

# Clean up temporary files and builds
clean:
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -r {} +

# Build package
build:
	$(POETRY) build

# Publish to Test PyPI
publish-test:
	$(POETRY) config pypi-token.pypi $$PYPI_TOKEN
	$(POETRY) config repositories.testpypi https://test.pypi.org/legacy/
	$(POETRY) publish -r testpypi

# Publish to PyPI
publish:
	$(POETRY) config pypi-token.pypi $$PYPI_TOKEN
	$(POETRY) publish

# Setup local development environment
dev-setup:
	curl -sSL https://install.python-poetry.org | python3 -
	$(POETRY) config virtualenvs.in-project true
	$(POETRY) install
	git init
	git add .
	git commit -m "Initial commit"

# Install package locally in editable mode
develop:
	pip install -e .