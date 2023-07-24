from flask import (
    Flask, render_template, request, redirect, url_for, flash
)
import os
import requests
from dotenv import load_dotenv
from validators import url as validate
from urllib.parse import urlparse
import page_analyzer.html_parse as html_parse
import page_analyzer.db as db

app = Flask(__name__)

# export env_vars for dev-server
if "SECRET_KEY" not in os.environ:
    load_dotenv()
app.secret_key = os.getenv('SECRET_KEY', 'SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL', 'DATABASE_URL')

db.import_sql(DATABASE_URL, f'{os.path.dirname(__file__)}/database.sql')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls/', methods=['GET', 'POST'])
def urls():

    if request.method == 'GET':
        join_raws = db.select_distinct_join_desc(DATABASE_URL)
        return render_template('urls/index.html', raws=join_raws)

    if request.method == 'POST':
        data = request.form.to_dict()['url']
        if not validate(data):
            flash('Некорректный URL', 'danger')
            return render_template('index.html', url=data), 422
        parsed_data = urlparse(data)
        url_normal = ''.join([parsed_data.scheme, '://', parsed_data.hostname])
        urls_raw = db.select_url_where(DATABASE_URL, url_normal)
        if not urls_raw:
            db.insert_to_urls(DATABASE_URL, url_normal)
            urls_raw = db.select_url_where(DATABASE_URL, url_normal)
            flash('Страница успешно добавлена', 'success')
        else:
            flash('Страница уже существует', 'info')
        return redirect(url_for('url', id=urls_raw['id']))


@app.get('/url/<id>')
def url(id):
    urls_raw = db.select_url_where(DATABASE_URL, id, column='id')
    url_checks = db.select_url_checks_desc(DATABASE_URL, id)
    return render_template(
        'urls/show.html',
        urls_raw=urls_raw,
        url_checks=url_checks)


@app.post('/urls/<id>/checks')
def url_checks(id):
    urls_raw = db.select_url_where(DATABASE_URL, id, column='id')
    try:
        request = requests.get(urls_raw['name'], timeout=2)
    except (
        requests.Timeout, requests.ConnectionError, requests.HTTPError,
    ):
        flash('Произошла ошибка при проверке', 'danger')
    else:
        seo_data = html_parse.get_seo(request.text)
        db.insert_to_url_checks(
            DATABASE_URL, id, request.status_code, seo_data)
        flash('Страница успешно проверена', 'success')
    finally:
        return redirect(url_for('url', id=id))
