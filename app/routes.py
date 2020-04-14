from flask import render_template
from app import app


@app.route('/')
def index_():
    user = {'username': 'MUTT'}
    return render_template('index.html', title='Home', user=user)
