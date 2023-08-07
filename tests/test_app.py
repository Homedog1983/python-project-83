import pytest
import pook
from tests.conftest import (
    get_content_from, get_normalize_code_from)
from page_analyzer import app as tested_app


@pytest.fixture
def app():
    app = tested_app
    app.testing = True
    return app


@pytest.mark.parametrize(
    'index, test_urls, urls_checks, template_urls',
    [('index.json', 'test_urls.json',
        'urls_checks.json', 'template_urls.html')]
)
@pook.on
def test_app(app, index, test_urls, urls_checks, template_urls):
    with app.test_client() as client:
        # test index:
        response = client.get("/")
        response_text = response.text
        for phrase in get_content_from(index):
            assert phrase in response_text

        # test_urls_post:
        for url in get_content_from(test_urls):
            response = client.post(
                '/urls', data={"url": url['name']},
                follow_redirects=True)
            assert response.status_code == url['expected_code']
            assert len(response.history) == url['expected_redirect']
            assert response.request.path == url['expected_path']
            assert url['expected_message'] in response.text

        # test url_checks:
        for check in get_content_from(urls_checks):
            pook.get(
                check['url'],
                reply=check['code'],
                response_type='text/plain',
                response_body=check['body']
            )
            response = client.post(
                f'/urls/{check["id"]}/checks', follow_redirects=True)
            assert len(response.history) == check['redirect']
            assert response.request.path == f"/urls/{check['id']}"
            assert check['message'] in response.text
            assert check['title'] in response.text
            assert check['description'] in response.text
            assert check['h1'] in response.text

        # test of resulting urls:
        expected_norm = get_normalize_code_from(
            get_content_from(template_urls), add_date=True)
        response = client.get('/urls')
        response_norm = get_normalize_code_from(response.text)
        assert expected_norm in response_norm
