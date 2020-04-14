from flask import Flask

application = Flask(__name__)


@application.route('/')
def index_():
    return 'Hello :)'


if __name__ == '__main__':
    application.debug = True
    application.run()
