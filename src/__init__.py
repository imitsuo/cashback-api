from flask import Flask
from flask_pymongo import PyMongo
from src.config import MONGO_URI

mongo = PyMongo()


def create_app(db_uri: str):
    app = Flask(__name__)

    if not db_uri:
        db_uri = MONGO_URI

    mongo.init_app(app, uri=db_uri, connect=True)

    from src.api import api_bp as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app
