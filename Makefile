install:
	poetry install
lint:
	poetry run flake8 page_analyzer
test:
	poetry run pytest -vv
test_s:
	poetry run pytest -vv -s
test-cov:
	poetry run pytest --cov=page_analyzer
test-coverage:
	poetry run pytest --cov-report xml --cov=page_analyzer
pgadmin:
	poetry run pgadmin4
dev:
	poetry run flask --app page_analyzer:app --debug run --port 8000
PORT ?= 8000
start:
	poetry run python -m gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
