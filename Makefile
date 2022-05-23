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

.PHONY: tailwind
tailwind:
	cd docs && npx tailwindcss -w -i ./examples/src.css -o ./docs/static/examples/tailwind.css

.PHONY: docs
docs:
	cd docs && mkdocs serve

.PHONY: examples
examples:
	cd docs && python examples.py
