from functools import wraps

from flask import request


def validate_api_token(validation_func):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kws):
            api_token = request.headers.get('Authorization')
            is_valid_api_token = validation_func(api_token)
            if is_valid_api_token:
                return f(*args, **kws)

            return 'Invalid API Token', 401

        return decorated_function

    return decorator
