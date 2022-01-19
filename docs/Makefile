.PHONY: deploy
deploy:
	mkdocs build
	rm site/assets/javascripts/lunr/min/lunr.*.min.js
	rsync --recursive --delete --progress site code:/var/www/jinjax/

.PHONY: tailwind
tailwind:
	tailwindcss -i ./docs/assets/css/_index.css -o ./docs/assets/css/index.css --watch
