# from . import create_app
from src import create_app, mongo


if __name__ == '__main__':
    app = create_app('')

    # @app.route("/a")
    # def hello_world():
    #     return "Hello, World!"

    result = mongo.db.revendedor.find_one()

    # from src.api import *

    app.run(host='0.0.0.0', port=23939, debug=True, threaded=True)
