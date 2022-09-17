from flask import jsonify, request
from flask_restful import abort, Resource
from .. import db_session, my_parsers
from ..users import User
from server import token_required
import logging

logging.basicConfig(level=logging.INFO)

parser = my_parsers.UserParser()


def abort_if_user_not_found(users_id):
    session = db_session.create_session()
    user = session.query(User).get(users_id)
    if not user:
        abort(404, message=f"User {users_id} not found")


def jsonify_user(user):
    user_dict = user.to_dict(only=['id', 'name', 'phone', 'cart', 'address_list', 'rank', 'image_path'])
    user_dict['cart'] = [{'products_id': assoc.products_id,
                          'product': assoc.product.to_dict(
                              only=('id', 'image_path', 'name', 'price', 'quantity', 'description',
                                    'retailers_id'))} for assoc in user.cart]
    user_dict['address_list'] = [address.to_dict(only=('id', 'name', 'city', 'street', 'house'))
                                 for address in user.address_list]
    return user_dict


class MyProfileResource(Resource):
    @token_required
    def get(self, token_data):
        users_id = token_data['user_id']
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(users_id)
        user_dict = jsonify_user(user)
        db_sess.close()
        return jsonify({'item': user_dict, 'status_code': 200})

    @token_required
    def delete(self, token_data):
        users_id = token_data['user_id']
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(users_id)
        if users_id < 3:
            return jsonify({'error': "you can't delete moderation"})
        db_sess.delete(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    @token_required
    def put(self, token_data):
        if not request.args:
            return jsonify({'error': 'Empty request'})
        users_id = token_data['user_id']
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(users_id)
        name = request.args['name'] if request.args.get('name') else user.name
        user.name = name
        user.rank = request.args['rank'] if request.args.get('rank') else user.rank
        db_sess.commit()
        db_sess.close()
        return jsonify({'status_code': '200'})


class UsersListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        return jsonify({'users': [user.to_dict(only=('id', 'phone', 'name', 'rank')) for user in users]})

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        if request.json.get('id') and request.json.get('id') in [user.id for user in db_sess.query(User).all()]:
            return jsonify({'error': 'Id already exists'})
        if request.json.get('phone') and request.json.get('phone') in [user.phone for user
                                                                       in db_sess.query(User).all()]:
            return jsonify({'error': 'user with this phone number already exists'})
        user = User()
        if args.get('id'):
            user.id = args.get('id')
        user.phone = args['phone']
        # user.name = args['name']

        db_sess.add(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})

# class UsersSearchResource(Resource):
#     def get(self, to_find):
#         db_sess = db_session.create_session()
#         search_like = f"%{'%'.join(to_find.split())}%"
#         users = db_sess.query(User).filter(User.nickname.like(search_like) | User.name.like(search_like) |
#                                            User.surname.like(search_like)).all()
#         return jsonify({'users': [user.to_dict(only=('id', 'nickname', 'surname', 'name', 'rank', 'avatar'))
#                                   for user in users]})
#
#
# class UsersSubscriptionsResource(Resource):
#     def get(self, from_for, users_id):
#         abort_if_user_not_found(users_id)
#         db_sess = db_session.create_session()
#         user = db_sess.query(User).get(users_id)
#         if from_for == 'for':
#             subscriptions = [sub.id for sub in user.subscribed]
#         else:
#             subscriptions = [sub.id for sub in user.subscribes]
#         logging.info(subscriptions)
#         users = db_sess.query(User).filter(User.id.in_(subscriptions)).all()
#         return jsonify({'users': [user.to_dict(only=('id', 'nickname', 'surname', 'name', 'rank', 'avatar'))
#                                   for user in users]})
#
#
# class UsersSubscribeResource(Resource):
#     def put(self, users_id, subscribers_id):
#         abort_if_user_not_found(users_id)
#         db_sess = db_session.create_session()
#         user = db_sess.query(User).get(users_id)
#         subscriber = db_sess.query(User).get(subscribers_id)
#         user.subscribed.append(subscriber)
#         db_sess.commit()
#         return jsonify({'success': 'OK'})
#
#     def delete(self, users_id, subscribers_id):
#         abort_if_user_not_found(users_id)
#         db_sess = db_session.create_session()
#         user = db_sess.query(User).get(users_id)
#         subscriber = db_sess.query(User).get(subscribers_id)
#         user.subscribed.remove(subscriber)
#         db_sess.commit()
#         return jsonify({'success': 'OK'})
