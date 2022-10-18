.PHONY: test
test:
	pytest -x -vv tcom tests

.PHONY: lint
lint:
	flake8 --config=setup.cfg tcom tests

.PHONY: coverage
coverage:
	pytest --cov-config=pyproject.toml --cov-report html --cov tcom tcom tests

.PHONY: types
types:
	pyright tcom

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

.PHONY: docs.build
docs.build:
	cd docs && mkdocs build
	rm docs/site/assets/javascripts/lunr/min/lunr.ar.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.da.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.de.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.du.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.es.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.fi.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.fr.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.hi.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.hu.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.it.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.ja.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.jp.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.nl.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.no.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.pt.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.ro.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.ru.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.sv.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.th.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.tr.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.vi.min.js
	rm docs/site/assets/javascripts/lunr/min/lunr.zh.min.js

.PHONY: examples
examples:
	cd docs && python examples.py
