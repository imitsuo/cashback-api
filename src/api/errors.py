from flask import jsonify
from marshmallow import ValidationError

from . import api_bp


class ApiValidationError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@api_bp.errorhandler(ValidationError)
def error_handler(error):
    response = jsonify(error.normalized_messages())
    response.status_code = 400
    return response


@api_bp.errorhandler(ApiValidationError)
def error_handler(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@api_bp.errorhandler(Exception)
def error_handler(error):
    response = jsonify({'message': 'something went wrong'})
    response.status_code = 500
    return response
