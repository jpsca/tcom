.PHONY: test
test:
	pytest -x jinjax tests

.PHONY: lint
lint:
	flake8 --config=setup.cfg jinjax tests

.PHONY: coverage
coverage:
	pytest --cov-config=.coveragerc --cov-report html --cov jinjax jinjax tests

.PHONY: install
install:
	pip install -e .[test,dev]
	# pip install -r docs/requirements.txt
	# pre-commit install
