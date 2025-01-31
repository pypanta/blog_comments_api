import datetime


def set_cookie(response, key, token, time_valid):
    days, hours, minutes, seconds = time_valid
    # Convert to seconds
    max_age = days * 86400 + hours * 3600 + minutes * 60 + seconds
    expires_time = (
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age)
    ).strftime("%a, %d-%b-%Y %H:%M:%S GMT")

    # Manually set Partitioned attribute (not directly supported in Flask)
    response.headers.add(
        'Set-Cookie',
        f'{key}={token}; HttpOnly; SameSite=None; Secure; Partitioned; Path=/; Max-Age={max_age}; Expires={expires_time}'
    )
    return response


def delete_cookie(response, key):
    response.headers.add(
        'Set-Cookie',
        f'{key}=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0; HttpOnly; SameSite=None; Secure; Path=/; Partitioned;'
    )
    return response
