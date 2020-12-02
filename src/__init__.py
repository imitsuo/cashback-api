from flask import Flask
from flask_pymongo import PyMongo

mongo_uri = 'mongodb://mongoadmin:secret@localhost:27017/cashback-api?authSource=admin&authMechanism=SCRAM-SHA-1'
mongo = PyMongo()


def create_app(db_uri: str):
    app = Flask(__name__)
    # app.config['MONGO_URI'] = mongo_uri

    if not db_uri:
        db_uri = mongo_uri

    mongo.init_app(app, uri=db_uri, connect=True)

    from src.api import api_bp as api_blueprint
    app.register_blueprint(api_blueprint) #, url_prefix='/api/v1'

    return app
