from flask import (
    Flask, render_template, request, redirect, url_for, flash)
from dotenv import load_dotenv
from validators import url as validate
import os
import requests
import page_analyzer.parse as parse
import page_analyzer.db as db

if "SECRET_KEY" not in os.environ:
    load_dotenv()

ROOT_DIR = f'{os.path.dirname(__file__)}/..'
db.import_sql(f'{ROOT_DIR}/database.sql')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls_get():
    urls = db.get_urls_with_last_check_info()
    return render_template('urls/index.html', urls=urls)


@app.post('/urls')
def urls_post():
    data = request.form["url"]
    if not validate(data):
        flash('Некорректный URL', 'danger')
        return render_template('index.html', url=data), 422
    url_normal = parse.get_normalize_url(data)
    url = db.get_url_by_attrs({'column': 'name', 'data': url_normal})
    if url:
        id = url['id']
        flash('Страница уже существует', 'info')
    else:
        id = db.add_url(url_normal)
        flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url', id=id))


@app.get('/urls/<id>')
def url(id):
    url = db.get_url_by_attrs({'column': 'id', 'data': id})
    url_checks = db.get_url_checks_by(id)
    return render_template(
        'urls/show.html',
        url=url,
        url_checks=url_checks)


@app.post('/urls/<id>/checks')
def url_checks(id):
    url = db.get_url_by_attrs({'column': 'id', 'data': id})
    url_name = url['name']
    try:
        response = requests.get(url_name, timeout=5)
    except (
        requests.Timeout, requests.ConnectionError,
        requests.HTTPError, requests.RequestException
    ) as e:
        print(f'Произошла ошибка при проверке: {e}')
        flash('Произошла ошибка при проверке', 'danger')
    else:
        if response.status_code != 200:
            flash('Произошла ошибка при проверке', 'danger')
        else:
            seo_data = parse.get_seo(response.text)
            db.add_url_check(id, response.status_code, seo_data)
            flash('Страница успешно проверена', 'success')
    finally:
        return redirect(url_for('url', id=id))
