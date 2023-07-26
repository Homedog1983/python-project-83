import pytest
import os
from page_analyzer import app as tested_app
from page_analyzer import import_sql


@pytest.fixture(autouse=True)
def app():
    app = tested_app
    # app = create_app('page_analyzer.app') - not return tested_app
    # for dev-machine
    if "DATABASE_URL_TEST" in os.environ:
        app.db_url = os.getenv("DATABASE_URL_TEST")
    app.testing = True
    import_sql(app.db_url, f'{os.path.dirname(__file__)}/../database.sql')
    return app


# example without parametrization etc


def test_request_example(app):
    with app.test_client() as client:
        response = client.get("/")
        assert 'href="/">Анализатор страниц</a>' in response.text
        assert 'href="/urls">Сайты</a>' in response.text
        assert '>Анализатор страниц</h1>' in response.text
