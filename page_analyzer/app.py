from flask import (
    Flask, render_template, request, redirect, url_for, flash,
)
from dotenv import load_dotenv
from validators import url as validate
from urllib.parse import urlparse
import os
import requests
import page_analyzer.html_parse as html_parse
import page_analyzer.db as db


app = Flask(__name__)

# export env_vars for dev-server
if "SECRET_KEY" not in os.environ:
    load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

db.import_sql(DATABASE_URL, f'{os.path.dirname(__file__)}/../database.sql')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['GET', 'POST'])
def urls():

    if request.method == 'GET':
        join_raws = db.select_distinct_join_desc(DATABASE_URL)
        return render_template('urls/index.html', raws=join_raws)

    if request.method == 'POST':
        data = request.form["url"]
        if not validate(data):
            flash('Некорректный URL', 'danger')
            return render_template('index.html', url=data), 422
        parsed_data = urlparse(data)
        url_normal = ''.join([parsed_data.scheme, '://', parsed_data.hostname])
        urls_raw = db.select_url_where(DATABASE_URL, url_normal)
        if urls_raw:
            id = urls_raw['id']
            flash('Страница уже существует', 'info')
        else:
            id = db.insert_to_urls(DATABASE_URL, url_normal)
            flash('Страница успешно добавлена', 'success')
        return redirect(url_for('url', id=id))


@app.get('/urls/<id>')
def url(id):
    urls_raw = db.select_url_where(DATABASE_URL, id)
    url_checks = db.select_url_checks_desc(DATABASE_URL, id)
    return render_template(
        'urls/show.html',
        urls_raw=urls_raw,
        url_checks=url_checks)


@app.post('/urls/<id>/checks')
def url_checks(id):
    urls_raw = db.select_url_where(DATABASE_URL, id)
    try:
        request = requests.get(urls_raw['name'], timeout=2)
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
            db.insert_to_url_checks(
                DATABASE_URL, id, request.status_code, seo_data)
            flash('Страница успешно проверена', 'success')
    finally:
        return redirect(url_for('url', id=id))
