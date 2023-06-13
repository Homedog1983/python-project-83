PORT ?= 8000
install:
	poetry install
build:
	poetry build
publish:
	poetry publish --dry-run
package-install:
	python3 -m pip install --user dist/*.whl
lint:
	poetry run flake8 page-analyzer
dev:
	poetry run flask --app page_analyzer run
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer