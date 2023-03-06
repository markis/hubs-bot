PWD := "."
INSTALL_STAMP := .install.stamp

all: lint test build

install:
	poetry install

lint:
	poetry run ruff check ${PWD}
	poetry run black --check ${PWD}
	poetry run mypy ${PWD}

fix:
	poetry run ruff check --fix ${PWD}
	poetry run black ${PWD}

test:
	poetry run coverage run -m pytest
	poetry run coverage report -m
	poetry run coverage html

build:
	pip install --disable-pip-version-check build wheel
	python -m build --wheel

clean:
	poetry env remove --all
	rm -rf build dist htmlcov *.egg-info
	find . -name "*.pyc" -delete

.PHONY: venv lint test build clean
