import urllib.parse
import uuid
from functools import wraps

from flask import session, flash, redirect, url_for


def login_required(method):
    @wraps(method)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return method(*args, **kwargs)
        else:
            flash('You need to log in first.')
            return redirect(url_for('user.login'))
    return wrap


def get_id():
    return int(str(int(uuid.uuid4()))[0:10])


def url_encode_tag(a_str):
    return urllib.parse.quote(a_str, safe='')


def url_decode_tag(a_str):
    return urllib.parse.unquote(a_str)


def make_decoded(a_str):
    if '%' in a_str:
        return url_decode_tag(a_str)
    else:
        return a_str


def make_encoded(a_str):
    """
    Check is a string needs encoding.

    If it does return it encoded.

    If not return it unencoded.
    """
    forbidden = [";", "/", "?", ":", "@", "=", "&", '"', "'", "<", ">",
                 "#", "{", "}", "|", "\\", "/", "^", "~", "[", "]", "`", " "]
    for char in a_str:
        if char in forbidden:
            print(a_str, ' needs encoding')
            return url_encode_tag(a_str)

    return a_str
