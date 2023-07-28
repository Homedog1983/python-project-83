from flask import (
    Flask, render_template, request, redirect, url_for, flash)
from dotenv import load_dotenv
from validators import url as validate
from urllib.parse import urlparse
import os
import requests
import page_analyzer.html_parse as html_parse
import page_analyzer.db as db

if "SECRET_KEY" not in os.environ:
    load_dotenv()
db.import_sql(f'{os.path.dirname(__file__)}/../database.sql')

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
    parsed_data = urlparse(data)
    flash(f'parsed_data = {parsed_data}')  # test mes for deploy
    url_normal = ''.join([parsed_data.scheme, '://', parsed_data.hostname])
    flash(f'url_normal = {url_normal}')  # test mes for deploy
    url = db.get_url_by_attrs({'column': 'name', 'data': url_normal})
    flash(f'url = {url}')  # test mes for deploy
    if url:
        id = url['id']
        flash('Страница уже существует', 'info')
    else:
        id = db.add_url(url_normal)
        flash('Страница успешно добавлена', 'success')
    flash(f'id ater if = {id}')  # test mes for deploy
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
    flash(f'url = {url}')  # test mes for deploy
    url_name = url['name']
    try:
        request = requests.get(url_name, timeout=5)
    except (
        requests.Timeout, requests.ConnectionError,
        requests.HTTPError, requests.RequestException
    ) as e:
        flash(f'except: {e}')  # test mes for deploy
        print(f'except: {e}')
        flash('Произошла ошибка при проверке', 'danger')
    else:
        if request.status_code != 200:
            flash('sc != 200')  # test mes for deploy
            flash('Произошла ошибка при проверке', 'danger')
        else:
            seo_data = html_parse.get_seo(request.text)
            flash(f'seo = {seo_data}')  # test mes for deploy
            db.add_url_check(id, request.status_code, seo_data)
            flash('Страница успешно проверена', 'success')
    finally:
        return redirect(url_for('url', id=id))
