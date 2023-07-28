import pytest
import os
import pook
from tests.conftest import (
    get_content_from, get_normalize_code_from)
from page_analyzer import app as tested_app
from page_analyzer import import_sql


# Каждый следующий тест зависит от предыдущего (наполняется БД)
# Идемпотентность достигается автоматическим обновлением таблиц
# вначала тестовой сессии


import_sql(f'{os.path.dirname(__file__)}/../database.sql')
app = tested_app
app.testing = True


def test_index_get():
    with app.test_client() as client:
        response = client.get("/")
        assert 'href="/">Анализатор страниц</a>' in response.text
        assert 'href="/urls">Сайты</a>' in response.text
        assert '>Анализатор страниц</h1>' in response.text


@pytest.mark.parametrize(
    'url, code, redirect, message, path', [
        ('asfg', 422, 0, 'Некорректный URL', '/urls'),
        ('http://hexlet.io/', 200, 1, 'Страница успешно добавлена', '/urls/1'),
        ('http://hexlet.io/sdf', 200, 1, 'Страница уже существует', '/urls/1'),
        ('http://wrong.com', 200, 1, 'Страница успешно добавлена', '/urls/2'),
        ('http://vc.com/fgh', 200, 1, 'Страница успешно добавлена', '/urls/3'),
    ])
def test_urls_post(url, code, redirect, message, path):
    with app.test_client() as client:
        response = client.post(
            '/urls', data={"url": url}, follow_redirects=True)
        assert response.status_code == code
        assert len(response.history) == redirect
        assert response.request.path == path
        assert message in response.text


@pytest.mark.parametrize(
    "id, data_path", [
        (1, "url_checks_1.json"),
        (2, "url_checks_2.json"),
        (3, "url_checks_3.json")
    ])
@pook.on
def test_url_checks(id, data_path):
    data = get_content_from(data_path)
    pook.get(
        data['url'],
        reply=data['code'],
        response_type='text/plain',
        response_body=data['body']
    )
    with app.test_client() as client:
        response = client.post(
            f'/urls/{id}/checks', follow_redirects=True)
        assert len(response.history) == data['redirect']
        assert response.request.path == f"/urls/{data['id']}"
        assert data['message'] in response.text
        assert data['title'] in response.text
        assert data['description'] in response.text
        assert data['h1'] in response.text


@pytest.mark.parametrize("template_path", ["urls.html"])
def test_urls_get(template_path):
    expected_norm = get_normalize_code_from(
        get_content_from(template_path), add_date=True)
    with app.test_client() as client:
        response = client.get('/urls')
        response_norm = get_normalize_code_from(response.text)
        assert expected_norm in response_norm
