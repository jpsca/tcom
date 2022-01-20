.PHONY: test
test:
	pytest -x oot tests

.PHONY: lint
lint:
	flake8 --config=setup.cfg oot tests

.PHONY: coverage
coverage:
	pytest --cov-config=.coveragerc --cov-report html --cov oot oot tests

.PHONY: types
types:
	mypy oot

.PHONY: install
install:
	pip install -e .[test,dev]
	pip install -r docs/requirements.txt
	# pre-commit install
