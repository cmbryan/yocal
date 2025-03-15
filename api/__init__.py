from flask import Flask


def create_app(*args, **kwargs):
    app = Flask(__name__)
    return app
