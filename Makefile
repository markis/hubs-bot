PWD := "."
.PHONY: venv lint test build clean

all: install lint test

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
	poetry run pytest --cov-report html

clean:
	poetry env remove --all
	rm -rf build dist htmlcov *.egg-info
	find . -name "*.pyc" -delete
