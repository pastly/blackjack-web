import os


def postgres_uri():
    e = os.environ
    # the fallback options here are for my local development machine
    host = e.get('RDS_HOSTNAME') or 'localhost'
    port = e.get('RDS_PORT') or '5432'
    db_name = e.get('RDS_DB_NAME') or 'blackjack'
    user = e.get('RDS_USERNAME') or 'matt'
    pw = e.get('RDS_PASSWORD') or 'AMEctYKRSdJupDnEfAZdVC4G'
    return f'postgresql://{user}:{pw}@{host}:{port}/{db_name}'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mNTYdSyk7278xjVku8WSactJ'
    SQLALCHEMY_DATABASE_URI = postgres_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False