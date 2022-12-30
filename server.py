import os
import random
import string
from datetime import datetime, timedelta
from functools import wraps

from PIL import Image
from flask import Flask, request, jsonify, url_for
from flask_restful import Api, abort
from requests import post
from werkzeug.serving import WSGIRequestHandler
from werkzeug.utils import secure_filename

from flask_ipban import IpBan

import jwt

import image_cutter
from data import db_session, users, events
from data.resources.__all_resources import *

import logging

from call_manager import CallTransport

logging.basicConfig(level=logging.WARNING)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('TOOK_SECRET_KEY', 'raise error')
assert app.config['SECRET_KEY'] != 'raise error'
path = 'https://localhost:8080'
api = Api(app)
ip_ban = IpBan(app)
ip_ban.url_pattern_add('^/api/auth/get_code$', match_type='regex')
ip_ban.url_pattern_add('^/api/auth/log_in$', match_type='regex')

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']


def main():
    db_session.global_init('Akhmed', 'Akhmedik2005', 'localhost:3306', "meroplan")
    api.add_resource(user_resource.MyProfileResource, '/api/my_profile')
    api.add_resource(user_resource.UsersResource, '/api/users/<users_id>')
    api.add_resource(user_resource.SubscribeResource, '/api/subscribe/<users_id>')
    api.add_resource(user_resource.MemberResource, '/api/member/<events_id>')

    api.add_resource(event_resource.EventsResource, '/api/events/<events_id>')
    api.add_resource(event_resource.EventsListResource, '/api/events', endpoint='/events')

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
            return jsonify({'message': 'Token is missing !!', 'result': '401'})
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS512'])
        if datetime.fromisoformat(data['expires_at']) < datetime.now():
            print(datetime.fromisoformat(data['expires_at']))
            print(datetime.now())
            return jsonify({'message': 'token already expired', 'result': '401'})
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
    # call_manager = CallTransport("ed7749c50f8e4bba7353c72e18321bf2")
    # response = call_manager.send(phone_number)
    # if response.result == 'ok':
    #     code = response.code
    # else:
    #     abort(404, message=response.error_code, result=response.result)
    #     return

    code = 1000

    token = jwt.encode({
        'code': code,
        'phone': phone_number,
        'expires_at': (datetime.now() + timedelta(minutes=5)).isoformat()
        }, app.config['SECRET_KEY'], algorithm='HS512')
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
    new_user = False
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
        new_user = True
    token = jwt.encode({
        'user_id': user.id,
        'user_secret': user.secret,
        'phone': user.phone,
        'expires_at': (datetime.utcnow() + timedelta(weeks=4)).isoformat()
    }, app.config['SECRET_KEY'], algorithm='HS512')

    return jsonify({'auth_token': token, 'new_user': new_user, 'result': 'ok'})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('uploaded_file',
#                                     filename=filename))
#
#
# @app.route('/post_event/<img:image>', methods=['POST'])
# @token_required
# def event_posting(token_data):
#     db_sess = db_session.create_session()
#     event = events.Event()
#     rand_id = ''.join(random.choices(string.digits + string.ascii_letters + '-_', k=8))
#     while rand_id in db_sess.query(events.Event.id).all():
#         rand_id = ''.join(random.choices(string.digits + string.ascii_letters + '-_', k=8))
#     event.id = rand_id
#     file_code = secure_filename(f'{str(rand_id) + "-" + str(token_data["user_id"])}.png')
#     filepath = f'static/img/events/{file_code}'
#     if os.path.exists(filepath):
#         os.remove(filepath)
#     file = request.files['file']
#     logging.info(filepath)
#     if file and allowed_file(file.filename):
#         file.save(filepath)
#         image = Image.open(filepath)
#         image.crop(image_cutter.get_central_rect(image.size, (328, 106)))
#         image.save(filepath)
#         image.close()
#         logging.info('success')
#     req = post(path + '/api/events',
#                json={'name': form.title.data,
#                      'photo': url_for('static',
#                                       filename=f'img/events/{file_code}'),
#                      'description': form.description.data,
#                      'author': current_user.id}).json()
#     logging.info(str(req))
#     return redirect('/publications')
#     return render_template('post_publication.html', title='Публикация', form=form)


if __name__ == '__main__':
    main()
