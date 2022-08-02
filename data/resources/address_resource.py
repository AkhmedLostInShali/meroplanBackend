from flask import jsonify, request
from flask_restful import abort, Resource
from .. import db_session, my_parsers
from ..address import Address
import logging
import datetime

logging.basicConfig(level=logging.INFO)

parser = my_parsers.AddressParser()


def abort_if_address_not_found(address_id):
    session = db_session.create_session()
    comment = session.query(Address).get(address_id)
    if not comment:
        abort(404, message=f"Address {address_id} not found")


class AddressesResource(Resource):
    def get(self, address_id):
        abort_if_address_not_found(address_id)
        db_sess = db_session.create_session()
        address = db_sess.query(Address).get(address_id)
        out_dict = address.to_dict(only=('id', 'name', 'city', 'street', 'house', 'flat', 'entrance', 'level',
                                         'comment', 'owner_id'))
        return jsonify({'address': out_dict})

    def delete(self, address_id):
        abort_if_address_not_found(address_id)
        db_sess = db_session.create_session()
        address = db_sess.query(Address).get(address_id)
        # if users_id < 3:
        #     return jsonify({'error': "you can't delete moderation"})
        db_sess.delete(address)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def put(self, address_id):
        abort_if_address_not_found(address_id)
        if not request.json:
            return jsonify({'error': 'Empty request'})
        db_sess = db_session.create_session()
        address = db_sess.query(Address).get(address_id)

        address.name = request.json['name'] if request.json.get('name') else address.name
        address.city = request.json['city'] if request.json.get('city') else address.city
        address.street = request.json['street'] if request.json.get('street') else address.street
        address.house = request.json['house'] if request.json.get('house') else address.house
        address.flat = request.json['flat'] if request.json.get('flat') else address.flat
        address.entrance = request.json['entrance'] if request.json.get('entrance') else address.entrance
        address.level = request.json['level'] if request.json.get('level') else address.level
        address.comment = request.json['comment'] if request.json.get('comment') else address.comment

        db_sess.commit()
        return jsonify({'success': 'OK'})


class AddressesListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        addresses = db_sess.query(Address).all()
        return jsonify({'comments': [address.to_dict(only=('id', 'name', 'city', 'street', 'house', 'flat', 'entrance',
                                                           'level', 'comment', 'owner_id'))
                                     for address in addresses]})

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        address = Address()
        address.name = args['name']
        address.city = args['city']
        address.street = args['street']
        address.house = args['house']
        address.flat = args.get('flat')
        address.entrance = args.get('entrance')
        address.level = args.get('level')
        address.comment = args.get('comment')
        address.owner_id = args['owner_id']

        db_sess.add(address)
        db_sess.commit()
        return jsonify({'success': 'OK'})


# class CommentsTreeResource(Resource):
#     def get(self, publications_id):
#         db_sess = db_session.create_session()
#         comments = db_sess.query(Comment).filter(Comment.receiver == publications_id).all()
#         out_list = []
#         for comment in comments:
#             out_dict = comment.to_dict(only=('id', 'text', 'send_time', 'receiver'))
#             out_dict['user'] = comment.user.to_dict(only=('id', 'nickname', 'avatar'))
#             out_list.append(out_dict)
#         return jsonify({'comments': out_list})
