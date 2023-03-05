PWD := "."
VENV := "venv"

all: lint test build

venv: venv/touchfile

venv/touchfile: pyproject.toml
	test -d ${VENV} || python -m venv ${VENV}
	. ${VENV}/bin/activate; (\
		pip install --disable-pip-version-check ".[dev]";\
	)
	touch venv/touchfile

lint: venv
	@. ${VENV}/bin/activate;(\
		ruff check "${PWD}" ;\
		black --check "${PWD}" ;\
	)

fix: venv
	@. ${VENV}/bin/activate; (\
		ruff check --fix "${PWD}" ;\
		black "${PWD}" ;\
	)

test: venv
	@. ${VENV}/bin/activate;(\
		coverage run;\
		coverage report -m;\
		coverage html;\
	)

build:
	@test -d venv || python -m venv venv
	@. ${VENV}/bin/activate; (\
		pip install --disable-pip-version-check -U ".[dev]";\
		python -m build --wheel;\
	)

clean:
	@rm -rf ${VENV} build dist htmlcov *.egg-info
	@find . -name "*.pyc" -delete

.PHONY: venv lint test build clean
