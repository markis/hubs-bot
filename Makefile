.PHONY: venv ruff mypy lint test build clean

VENV_NAME?=venv
PYTHON?=$(VENV_NAME)/bin/python3
PWD?="."
.DEFAULT_GOAL := all

# Aliases
all: venv lint test
check: lint
lint: ruff mypy
format: fix

# Create the virtual environment
# This target ensures that the virtual environment is only created or updated when
# the requirements.txt or requirements_dev.txt files have changed.
venv: $(VENV_NAME)/bin/activate
$(VENV_NAME)/bin/activate: pyproject.toml
	test -d $(VENV_NAME) || python3 -m venv $(VENV_NAME)
	$(MAKE) install-requirements
	touch $(VENV_NAME)/bin/activate

install-requirements:
	$(PYTHON) -m pip install ".[dev,test]"

test: venv
	$(PYTHON) -m pytest --cov-report html --cov-report term

ruff: venv
	$(PYTHON) -m ruff check ${PWD}
	$(PYTHON) -m ruff format --check ${PWD}

mypy: venv
	$(PYTHON) -m mypy ${PWD}

fix:
	$(PYTHON) -m ruff check --fix ${PWD}
	$(PYTHON) -m ruff format ${PWD}

clean:
	rm -r $(VENV_NAME)
	rm -rf build dist htmlcov *.egg-info
	find . -name "*.pyc" -delete
