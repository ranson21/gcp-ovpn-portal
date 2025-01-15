.PHONY: install run test lint format clean build publish-test publish dev-setup

# Poetry as the package manager
POETRY = poetry

# Define the default version as an empty string if not provided
NEW_VERSION ?=

# Install dependencies
install:
	$(POETRY) install

# Run local version
run:
	$(POETRY) run ovpn-portal

# Run development server
dev:
	@mkdir -p tmp/logs
	$(POETRY) run dev

# Run tests
test:
	$(POETRY) run pytest tests/ -v

# Run tests with coverage
coverage:
	$(POETRY) run pytest --cov=ovpn_portal --cov-report=term-missing --cov-report=html --cov-report=xml:coverage.xml tests/
	$(POETRY) run python -m pip install codecov
	$(POETRY) run codecov -f coverage.xml
	@echo "Coverage report generated in coverage_html/index.html"

# Run linting
lint:
	$(POETRY) run isort --check-only src/ovpn_portal/ tests/
	$(POETRY) run black --check src/ovpn_portal/ tests/
	$(POETRY) run flake8 src/ovpn_portal/ tests/

# Format code
format:
	$(POETRY) run autoflake --in-place --remove-all-unused-imports --recursive .
	$(POETRY) run isort src/ovpn_portal/ tests/
	$(POETRY) run black src/ovpn_portal/ tests/

# Target to bump version in pyproject.toml
bump-version:
	$(POETRY) run python -m pip install toml
	$(POETRY) run python config/scripts/bump_version.py

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
	@echo "Starting build process..."
	@echo "Current directory: $$(pwd)"
	@cd src/ovpn_portal/static && echo "Static directory before npm: $$(pwd)" && npm install && npm run build
	@echo "Static assets build complete, returning to root: $$(pwd)"
	$(POETRY) build --verbose

# Publish to Test PyPI
publish-test:
	$(POETRY) config pypi-token.testpypi ${TEST_PYPI_TOKEN}
	$(POETRY) config repositories.testpypi https://test.pypi.org/legacy/
	$(POETRY) publish -r testpypi

# Publish to PyPI
publish:
	@if [ "$(PUBLISH)" != "true" ]; then \
		echo "Skipping PyPI publish for non-merge build"; \
	else \
		echo "Publishing to PyPI:"; \
		$(POETRY) config pypi-token.pypi ${PYPI_TOKEN}; \
		$(POETRY) publish; \
	fi

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