from flask import jsonify
from flask_restful import abort

from functools import wraps

from data.users import User

from .. import db_session


def check_api_key(key):
    if key != 'took_app_mobile':
        abort(403, message=f"Invalid apiKey")


def check_session_id(phone, session_id):
    session = db_session.create_session()
    user = session.query(User).get({'phone': phone})
    if not user.session_id:
        abort(403, message=f"User is not logged")
    elif user.session_id != session_id:
        abort(403, message=f"Invalid session_id")
    session.close()
