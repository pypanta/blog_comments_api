import datetime
from functools import wraps

import jwt

from flask import current_app, jsonify, request

from app.models import User


def create_token(identity, time_valid=(0, 0, 0, 60)):
    """
    Generates the Auth Token
    :return: string
    """
    days, hours, minutes, seconds = time_valid
    try:
        payload = {
            'exp': datetime.datetime.now(
                datetime.timezone.utc
            ) + datetime.timedelta(days=days,
                                   hours=hours,
                                   minutes=minutes,
                                   seconds=seconds),
            'iat': datetime.datetime.now(datetime.timezone.utc),
            'sub': identity
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e


def decode_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: string|bool
    """
    try:
        payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'),
                             algorithms='HS256')
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.cookies.get('access')
        decoded = decode_token(token)
        if decoded:
            user = User.query.filter_by(email=decoded).first()
            if user is not None:
                kwargs['user'] = user
                return f(*args, **kwargs)
        return jsonify({'message': 'Token is not valid or expired'}), 401
    return wrapper
