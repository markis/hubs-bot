PWD := "."
.PHONY: venv lint test build clean

all: install lint test
lint: ruff black mypy

install:
	poetry install

black:
	poetry run black --check ${PWD}

ruff:
	poetry run ruff check ${PWD}

mypy:
	poetry run mypy ${PWD}

fix:
	poetry run ruff check --fix ${PWD}
	poetry run black ${PWD}

test:
	@poetry run pytest --cov-report html --cov-report term

clean:
	poetry env remove --all
	rm -rf build dist htmlcov *.egg-info
	find . -name "*.pyc" -delete
