.PHONY: test
test:
	pytest -x tcom tests

.PHONY: lint
lint:
	flake8 --config=setup.cfg tcom tests

.PHONY: coverage
coverage:
	pytest --cov-config=.coveragerc --cov-report html --cov tcom tcom tests

.PHONY: types
types:
	mypy tcom

.PHONY: install
install:
	pip install -e .[test,dev]
	pip install -r docs/requirements.txt
	# pre-commit install
