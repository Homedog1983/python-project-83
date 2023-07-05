from flask import (
    Flask, render_template
    # request, redirect,
    # url_for, flash, get_flashed_messages, session
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
