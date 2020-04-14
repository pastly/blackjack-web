from flask import render_template
from app import app


@app.route('/')
def index_():
    user = {'username': 'MUTT'}
    i = len(app.config['SECRET_KEY'])
    return render_template('index.html', title='Home', user=user, i=i)
