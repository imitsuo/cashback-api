from functools import wraps

from flask import Blueprint, request, Response

api_bp = Blueprint('apis', __name__)


def validate_request_json():
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return Response('Content-type should be application/json', 400)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


from . import routes, errors

