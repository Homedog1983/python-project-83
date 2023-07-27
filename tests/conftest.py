import os
from page_analyzer import app as tested_app
from page_analyzer import import_sql


# @pytest.fixture(autouse=True)
def create_test_app():
    app = tested_app
    # for dev-machine
    if "DATABASE_URL_TEST" in os.environ:
        app.db_url = os.getenv("DATABASE_URL_TEST")
    app.testing = True
    import_sql(app.db_url, f'{os.path.dirname(__file__)}/../database.sql')
    return app


test_app = create_test_app()
