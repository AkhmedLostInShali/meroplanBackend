import os
import random
import string
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify
from flask_restful import Api, abort
from werkzeug.serving import WSGIRequestHandler

from flask_ipban import IpBan

import jwt

from data import db_session, users
from data.resources.__all_resources import *

import logging

from sms_manager import CallTransport

logging.basicConfig(level=logging.WARNING)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('TOOK_SECRET_KEY', 'raise error')
assert app.config['SECRET_KEY'] != 'raise error'
path = 'https://localhost:8080'
api = Api(app)
ip_ban = IpBan(app)
ip_ban.url_pattern_add('^/api/auth/get_code$', match_type='regex')
ip_ban.url_pattern_add('^/api/auth/log_in$', match_type='regex')


def main():
    db_session.global_init('Akhmed', 'Akhmedik2005', 'localhost:3306', "took")
    api.add_resource(user_resource.MyProfileResource, '/api/my_profile')

    api.add_resource(product_resource.ProductsResource, '/api/products/<int:products_id>')
    api.add_resource(product_resource.ProductsListResource, '/api/products', endpoint='/products')

    api.add_resource(retailer_resource.RetailersListResource, '/api/retailers')
    #
    api.add_resource(category_resource.CategoriesListResource, '/api/categories')
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(port=8080, host='127.0.0.1')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers.get('x-access-token')
        # return 401 if token is not passed
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        if datetime.fromisoformat(data['expires_at']) < datetime.now():
            print(datetime.fromisoformat(data['expires_at']))
            print(datetime.now())
            return jsonify({'message': 'token already expired', 'result': '401'}), 401
        # returns the current logged in users contex to the routes
        return f(token_data=data, *args, **kwargs)

    return decorated


@app.route('/api/auth/get_code', methods=['POST'])
def auth_get_code():
    phone_number = request.args.get('phone')
    if not phone_number:
        abort(403, message='Empty number argument', result='403')
        return
    print(phone_number)
    call_manager = CallTransport("ed7749c50f8e4bba7353c72e18321bf2")
    response = call_manager.send(phone_number)
    if response.result == 'ok':
        code = response.code
    else:
        abort(404, message=response.error_code, result=response.result)
        return

    # code = 1000

    token = jwt.encode({
        'code': code,
        'phone': phone_number,
        'expires_at': (datetime.now() + timedelta(minutes=5)).isoformat()
        }, app.config['SECRET_KEY'], algorithm='HS256')
    print((datetime.now() + timedelta(minutes=5)).isoformat())

    # return jsonify({'access_token': token, 'result': response.result})
    return jsonify({'access_token': token, 'result': 'ok'})


@app.route('/api/auth/log_in', methods=['POST'])
@token_required
def auth_log_in(token_data):
    input_code = request.args.get('code')
    if not input_code:
        abort(403, message='Empty code argument', result='403')
        return

    if str(input_code) != str(token_data['code']):
        return jsonify({'message': 'incorrect code', 'result': '401'}), 401
    session = db_session.create_session()
    user = session.query(users.User).filter(users.User.phone == token_data['phone']).first()
    if not user:
        user = users.User()
        user.phone = token_data['phone']
        rand_id = ''.join(random.choices(string.digits + string.ascii_letters + '-_', k=8))
        while rand_id in session.query(users.User.id).all():
            rand_id = ''.join(random.choices(string.digits + string.ascii_letters + '-_', k=8))
        user.id = rand_id
        user.set_secret(''.join(random.choices(string.printable, k=16)))
        session.add(user)
        session.commit()
        user = session.query(users.User).get(rand_id)
    token = jwt.encode({
        'user_id': user.id,
        'user_secret': user.secret,
        'phone': user.phone,
        'expires_at': (datetime.utcnow() + timedelta(weeks=4)).isoformat()
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'auth_token': token, 'result': 'ok'})


if __name__ == '__main__':
    main()
