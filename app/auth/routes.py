from flask import jsonify, make_response, request
from sqlalchemy.exc import IntegrityError

from app import db
from app.auth.tokens import decode_token, token_required
from app.models import User
from app.utils.cookie import delete_cookie, set_cookie

from . import bp
from .tokens import create_token
from .validators import validate


@bp.route('/register', methods=['POST'])
def register():
    """Register user"""
    data = request.get_json()

    for field in ('username', 'email', 'password', 'password_confirm'):
        if field not in data:
            return jsonify({f'message': f'{field} is required'}), 400

        is_valid = validate(field, data[field])

        if is_valid is not None:
            return jsonify({f'message': is_valid}), 400

    if data['password'] != data['password_confirm']:
        return jsonify({
            'message': 'Password and password confirm must be the same'
        }), 400,

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as e:
        if 'username' in e.args[0]:
            return jsonify({'message': 'Username is in use'}), 400
        elif 'email' in e.args[0]:
            return jsonify({'message': 'E-mail address is in use'}), 400

    return jsonify({'message': 'Success'}), 201


@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    # Filter user by email or username
    user = User.query.filter(
        (User.email == data.get('email'))
        | (User.username == data.get('email'))
    ).first()

    if user is not None:
        if user.check_password(data.get('password')):
            response = make_response()
            access_token = create_token(user.email)
            refresh_token = create_token(user.email, time_valid=(0, 12, 0, 0))
            set_cookie(response, 'access', access_token, (0, 0, 0, 60))
            set_cookie(response, 'refresh', refresh_token, (0, 12, 0, 0))

            if response.status_code == 200:
                return response

        return jsonify({'message': 'Wrong password!'}), 401

    return jsonify({'message': 'User not found!'}), 404


@bp.route('/logout', methods=['GET'])
@token_required
def logout(*args, **kwargs):
    """Logout user"""
    user = kwargs.get('user')
    if user is not None:
        response = make_response()
        delete_cookie(response, 'access')
        delete_cookie(response, 'refresh')
        return response
    return jsonify({'message': 'User not found!'}), 404


@bp.route('/user')
@token_required
def user_info(*args, **kwargs):
    """Get user informations"""
    user = kwargs.get('user')
    if user is not None:
        return jsonify(user.to_dict()), 200
    return jsonify({'message': 'User not found!'}), 404


@bp.route('/user-update', methods=['PATCH'])
@token_required
def user_update(*args, **kwargs):
    """Update user informations"""
    user = kwargs.get('user')
    if user:
        data = request.get_json()
        if not (email := data.get('email')):
            return jsonify({'message': 'E-mail is required field'}), 400
        if (password := data.get('password')) and (
            password_confirm := data.get('password_confirm')
        ):
            if password != password_confirm:
                return jsonify({
                    'message': 'Password and password confirm must be the same'
                }), 400
            if (valid := validate('password', password)) is not None:
                return jsonify({'message': valid}), 400
            user.set_password(password)
        user.username = data.get('username')
        user.about = data.get('about')
        # Set new auth tokens if user change e-mail address
        response = None
        if user.email != email:
            user.email = email
            response = make_response()
            access_token = create_token(user.email)
            refresh_token = create_token(user.email, time_valid=(0, 12, 0, 0))
            set_cookie(response, 'access', access_token, (0, 0, 0, 60))
            set_cookie(response, 'refresh', refresh_token, (0, 12, 0, 0))

        db.session.commit()

        if response:
            return response
        return jsonify(user.to_dict()), 200
    return jsonify({'message': 'User not found!'}), 404


@bp.route('/refresh', methods=['GET'])
def refresh():
    """Refresh token"""
    refresh_token = request.cookies.get('refresh')

    if refresh_token is None:
        return jsonify({'message': 'Unauthorized'}), 401

    payload = decode_token(refresh_token)

    user = User.query.filter_by(email=payload).first()

    if user is not None:
        response = make_response()
        access_token = create_token(user.email)
        set_cookie(response, 'access', access_token, (0, 0, 0, 60))
        return response

    return jsonify({'message': 'Unauthorized'}), 401
