import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mNTYdSyk7278xjVku8WSactJ'
