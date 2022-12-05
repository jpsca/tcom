.PHONY: test
test:
	poetry run pytest -x -vv tcom tests

.PHONY: lint
lint:
	poetry run flake8 tcom tests

.PHONY: coverage
coverage:
	poetry run pytest --cov-config=pyproject.toml --cov-report html --cov tcom tcom tests

.PHONY: types
types:
	poetry run pyright tcom

.PHONY: install
install:
	poetry install --with dev,test
	# pre-commit install

.PHONY: tailwind
tailwind:
	cd docs && npx tailwindcss -w -i ./examples/src.css -o ./docs/static/examples/tailwind.css

.PHONY: docs
docs:
	cd docs && python docs.py

.PHONY: docs.build
docs.build:
	cd docs && python docs.py build
