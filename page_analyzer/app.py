from flask import (
    Flask, render_template, request, redirect, url_for, flash)
from dotenv import load_dotenv
from validators import url as validate
from urllib.parse import urlparse
import os
import requests
import page_analyzer.html_parse as html_parse
import page_analyzer.db as db


def create_app(file_name: str):
    app = Flask(file_name)
    # export env_vars for dev-server
    if "SECRET_KEY" not in os.environ:
        load_dotenv()
    app.secret_key = os.getenv('SECRET_KEY')
    app.db_url = os.getenv('DATABASE_URL')
    return app


app = create_app(__name__)
db.import_sql(app.db_url, f'{os.path.dirname(__file__)}/../database.sql')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls_get():
    urls_data = db.get_urls_data(app.db_url)
    return render_template('urls/index.html', urls_data=urls_data)


@app.post('/urls')
def urls_post():
    data = request.form["url"]
    if not validate(data):
        flash('Некорректный URL', 'danger')
        return render_template('index.html', url=data), 422
    parsed_data = urlparse(data)
    url_normal = ''.join([parsed_data.scheme, '://', parsed_data.hostname])
    url_data = db.get_url_data_by(app.db_url, url_normal, 'name')
    if url_data:
        id = url_data['id']
        flash('Страница уже существует', 'info')
    else:
        id = db.add_url(app.db_url, url_normal)
        flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url', id=id))


@app.get('/urls/<id>')
def url(id):
    url_data = db.get_url_data_by(app.db_url, id, 'id')
    url_checks = db.get_url_checks_by(app.db_url, id)
    return render_template(
        'urls/show.html',
        url_data=url_data,
        url_checks=url_checks)


@app.post('/urls/<id>/checks')
def url_checks(id):
    url_data = db.get_url_data_by(app.db_url, id, 'id')
    url = url_data['name']
    try:
        request = requests.get(url, timeout=2)
    except (
        requests.Timeout, requests.ConnectionError, requests.HTTPError,
    ) as e:
        print(f'except: {e}')
        flash('Произошла ошибка при проверке', 'danger')
    else:
        if request.status_code != 200:
            flash('Произошла ошибка при проверке', 'danger')
        else:
            seo_data = html_parse.get_seo(request.text)
            db.add_url_check(
                app.db_url, id, request.status_code, seo_data)
            flash('Страница успешно проверена', 'success')
    finally:
        return redirect(url_for('url', id=id))
