from flask import (
    Flask, render_template, request, redirect, url_for, flash
)
import os
from dotenv import load_dotenv
import psycopg2
import page_analyzer.db as db
from validators import url as validate
from urllib.parse import urlparse


app = Flask(__name__)


if "SECRET_KEY" not in os.environ:  # export env for dev-server
    load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
db_connection = psycopg2.connect(os.getenv('DATABASE_URL'))
db_connection.autocommit = True
db.sql_load(db_connection, f'{os.path.dirname(__file__)}/database.sql')


@app.route('/')
def index():
    return render_template(
        'index.html',
        sc=app.secret_key[:5],
        conn=type(db_connection)
    )


@app.route('/urls/', methods=['GET', 'POST'])
def urls():

    if request.method == 'GET':
        # new table with parent table 'urls' ?
        # new collect-function with joined columns ?
        return render_template('urls/index.html')

    if request.method == 'POST':
        url = request.form.to_dict()['url']
        if not validate(url):
            flash('Некорректный URL', 'danger')
            return render_template('index.html', url=url), 422
        parsed_data = urlparse(url)
        url_normal = ''.join([parsed_data.scheme, '://', parsed_data.hostname])
        table_raw = db.collect_raw_filtered_by(db_connection, url_normal)
        if not table_raw:
            db.insert(db_connection, url_normal)
            table_raw = db.collect_raw_filtered_by(db_connection, url_normal)
            flash('Страница успешно добавлена', 'success')
        else:
            flash('Страница уже существует', 'info')
        return redirect(url_for('url', id=table_raw['id']))


@app.route('/url/<id>', methods=['GET', 'POST'])
def url(id):

    if request.method == 'GET':
        table_raw = db.collect_raw_filtered_by(db_connection, id, column='id')
        return render_template('urls/show.html', table_raw=table_raw)

    if request.method == 'POST':
        pass


@app.route('/url/<id>/checks', methods=['GET', 'POST'])
def url_checks(id):

    if request.method == 'GET':
        pass
    if request.method == 'POST':
        pass


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
