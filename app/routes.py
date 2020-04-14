from app import app


@app.route('/')
def index_():
    return 'Hello 2 :)'
