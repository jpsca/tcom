.PHONY: deploy
deploy:
	mkdocs build
	rm site/assets/javascripts/lunr/min/lunr.*.min.js
	rsync --recursive --delete --progress site code:/var/www/oot/

.PHONY: tailwind
tailwind:
	tailwindcss -i ./docs/_src/home.css -o ./docs/static/css/home.css --watch
