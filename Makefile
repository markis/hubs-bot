VENV := "venv"

venv: venv/touchfile

venv/touchfile: pyproject.toml
	test -d ${VENV} || python -m venv ${VENV}
	. ${VENV}/bin/activate; pip install ".[dev]"
	touch venv/touchfile

lint: venv
	@. ${VENV}/bin/activate; \
		ruff check . ; \
		black --check .

fix: venv
	@. ${VENV}/bin/activate; \
		ruff check --fix . ; \
		black .

test: venv
	@. ${VENV}/bin/activate; \
		coverage run ; \
		coverage report -m

build:
	@test -d venv || python -m venv venv
	@. ${VENV}/bin/activate; pip install -U ".[dev]"; python -m build

clean:
	@rm -rf ${VENV} build dist *.egg-info
	@find . -name "*.pyc" -delete

.PHONY: venv lint build test clean
