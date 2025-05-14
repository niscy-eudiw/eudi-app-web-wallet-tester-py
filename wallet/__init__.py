
import binascii
import os
import sys

from wallet.app_config.config import ConfService
sys.path.append(os.path.dirname(__file__))


from flask import Flask
from .V05_wallett import V05


def create_app():

    app = Flask(__name__)
    app.config['SECRET_KEY'] = generate_secret_key()

    app.register_blueprint(V05)


    return app

def generate_secret_key(length: int = 16) -> str:
    return binascii.hexlify(os.urandom(length)).decode()
