.PHONY: install run test lint format clean

# Python executable
PYTHON = python3
VENV = venv
BIN = $(VENV)/bin/

# Install all dependencies
install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)pip install --upgrade pip
	$(BIN)pip install -r requirements.txt

# Run development server
run:
	$(BIN)python -m flask run --debug --port 8081

# Run tests
test:
	$(BIN)pytest tests/ -v

# Run linting
lint:
	$(BIN)flake8 app/ tests/
	$(BIN)black --check app/ tests/
	$(BIN)isort --check-only app/ tests/

# Format code
format:
	$(BIN)black app/ tests/
	$(BIN)isort app/ tests/

# Clean up temporary files and virtual environment
clean:
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf $(VENV)