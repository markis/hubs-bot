.PHONY: build
build: venv pre-commit
	@pip install .
	@python setup.py build

.PHONY: lint
lint: pre-commit
	@pre-commit run --all-files

.PHONY: pre-commit
pre-commit:
	@command -v pre-commit >/dev/null || pip install pre-commit
	@pre-commit install -f --install-hooks

.PHONY: venv
venv:
	@test -d hubs_bot-venv || virtualenv -p python3 hubs_bot-venv
	@. hubs_bot-venv/bin/activate
	@python -m pip install --quiet --upgrade pip
	@pip install --quiet -Ur requirements-dev.txt

.PHONY: test
test:
	@command -v coverage >/dev/null || pip install coverage
	@coverage run --source="hubs_bot/" -m pytest tests/*_test.py
	@coverage report -m

.PHONY: clean
clean:
	@rm -rf hubs_bot-venv
	@find -iname "*.pyc" -delete
