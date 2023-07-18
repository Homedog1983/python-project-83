from flask import (
    Flask, render_template, request, redirect, url_for, flash
)
import os
from dotenv import load_dotenv
from validators import url as validate
from urllib.parse import urlparse
import requests
import page_analyzer.db as db

app = Flask(__name__)

# export env for dev- or deploy-server
if "SECRET_KEY" not in os.environ:
    load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

db.import_sql(DATABASE_URL, f'{os.path.dirname(__file__)}/database.sql')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls/', methods=['GET', 'POST'])
def urls():

    if request.method == 'GET':
        join_raws = db.select_join_desc(DATABASE_URL)
        return render_template('urls/index.html', raws=join_raws)

    if request.method == 'POST':
        url = request.form.to_dict()['url']
        if not validate(url):
            flash('Некорректный URL', 'danger')
            return render_template('index.html', url=url), 422
        parsed_data = urlparse(url)
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
        url_checks=url_checks
        )


@app.post('/urls/<id>/checks')
def url_checks(id):
    urls_raw = db.select_url_where(DATABASE_URL, id, column='id')
    try:
        request = requests.get(urls_raw['name'], timeout=2)
    except (
        requests.Timeout, requests.ConnectionError, requests.HTTPError
    ):
        flash('Произошла ошибка при проверке', 'danger')
    else:
        db.insert_to_url_checks(DATABASE_URL, id, request.status_code)
        flash('Страница успешно проверена', 'success')
    finally:
        return redirect(url_for('url', id=id))


# @app.route('/users/', methods=['GET', 'POST'])
# def users():
#     users = loads(request.cookies.get('users', dumps([])))
#     if request.method == 'GET':
#         messages = get_flashed_messages(with_categories=True)
#         term = request.args.get('term', '')
#         filtered_users = list(filter(lambda x: term in x['name'], users))
#         return render_template(
#             'users/index.html',
#             users=filtered_users,
#             search=term,
#             messages=messages
#         )
#     if request.method == 'POST':
#         new_user = request.form.to_dict()
#         errors = validate(new_user)
#         if errors:
#             return render_template(
#                 'users/new.html',
#                 user=new_user,
#                 errors=errors
#             ), 422
#         db.create(users, new_user)
#         flash(f'New user {new_user["name"]} was created!', 'success')
#         response = redirect(url_for('users'))
#         response.set_cookie('users', dumps(users))
#         return response


# @app.get('/users/<id>')
# def get_user(id):
#     users = loads(request.cookies.get('users', dumps([])))
#     user = db.get_user(users, int(id))
#     if user is None:
#         return "User not found", 404
#     return render_template(
#         'users/show.html',
#         user=user
#     )


# @app.get('/users/new')
# def new_user():
#     return render_template(
#         'users/new.html',
#         user={'name': '', 'email': ''},
#         errors={}
#     )


# @app.route('/users/<id>/edit', methods=['GET', 'POST'])
# def edit_user(id):
#     users = loads(request.cookies.get('users', dumps([])))

#     if request.method == 'GET':
#         user = db.get_user(users, int(id))
#         if user is None:
#             return "User not found", 404
#         return render_template(
#             'users/edit.html',
#             user=user,
#             errors={},
#         )

#     if request.method == 'POST':
#         user = request.form.to_dict()
#         errors = validate(user)
#         if errors:
#             return render_template(
#                 'users/edit.html',
#                 user=user,
#                 errors=errors,
#             ), 422
#         db.patch(users, user, int(id))
#         flash('User has been updated', 'success')
#         response = redirect(url_for('users'))
#         response.set_cookie('users', dumps(users))
#         return response


# @app.route('/users/<id>/delete', methods=['GET', 'POST'])
# def delete_user(id):
#     users = loads(request.cookies.get('users', dumps([])))

#     if request.method == 'GET':
#         return render_template(
#             'users/delete.html',
#             id=id,
#             current_user=session.get('user')
#         )
#     if request.method == 'POST':
#         db.delete(users, int(id))
#         flash('User has been deleted', 'success')
#         response = redirect(url_for('users'))
#         response.set_cookie('users', dumps(users))
#         return response
