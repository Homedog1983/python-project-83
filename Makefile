install:
	poetry install
lint:
	poetry run flake8 page_analyzer
dev:
	poetry run flask --app page_analyzer.app:app --debug run --port 8000
routes:
	poetry run flask --app page_analyzer.app routes
PORT ?= 8000
start:
	poetry run python -m gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer.app:app
pgadmin:
	poetry run pgadmin4