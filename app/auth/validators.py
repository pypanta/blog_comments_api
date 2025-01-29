import re


def validate_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, email):
        return None
    return 'E-mail address is not valid'


def validate_username(username):
    regex = r'\b\w{4,20}\b'
    if re.fullmatch(regex, username):
        return None
    return 'Username is not valid'


def validate_password(password):
    if password.isdigit():
        return 'Password is entirely numeric'
    if password.isalpha():
        return 'password is entirely alphabet'
    if len(password) < 4:
        return 'Password is less than 4 characters'
    if len(password) > 50:
        return 'Password is greater than 50 characters'
    return None


def validate(k, v):
    match k:
        case 'email':
            return validate_email(v)
        case 'username':
            return validate_username(v)
        case 'password':
            return validate_password(v)
        case _:
            return
