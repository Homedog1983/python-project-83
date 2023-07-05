from flask import (
    Flask, render_template, request, redirect,
    url_for
    # flash, get_flashed_messages, session
)
import os
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")


@app.route('/')
def index():
    return render_template(
        'index.html'
    )


@app.route('/urls/', methods=['GET', 'POST'])
def urls():
    if request.method == 'GET':
        return render_template(
            'urls/index.html'
        )
    if request.method == 'POST':
        # Валидация url.
        # Если некорректный url: сообщение об некорректности
        # и редирект на индекс
        # Если корректный, то проверка в БД на предмет совпадения,
        # если существует - сообщение о том, что уже есть и редирект на главную
        # Если прошло до этого этапа, то запись в БД + редирект на urls/<id>
        # new_url = request.form.to_dict()
        # errors = validate(new_url)
        # if errors:
        #     return render_template(
        #         'users/new.html',
        #         user=new_user,
        #         errors=errors
        #     ), 422
        # db.create(users, new_user)
        # flash(f'New user {new_user["name"]} was created!', 'success')
        # response = redirect(url_for('users'))
        # return response
        return redirect(url_for('urls'))


@app.route('/url/<id>', methods=['GET', 'POST'])
def url(id):
    if request.method == 'GET':
        return render_template(
            'urls/show.html'
        )
