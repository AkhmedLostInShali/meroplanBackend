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


class CommentsResource(Resource):
    def get(self, address_id):
        abort_if_address_not_found(address_id)
        db_sess = db_session.create_session()
        address = db_sess.query(Address).get(address_id)
        out_dict = address.to_dict(only=('id', 'text', 'send_time', 'receiver', 'sender'))
        out_dict['user'] = address.user.to_dict(only=('id', 'nickname', 'avatar'))
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
        address.text = request.json['text'] if request.json.get('text') else address.text
        db_sess.commit()
        return jsonify({'success': 'OK'})


class CommentsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        addresses = db_sess.query(Address).all()
        return jsonify({'comments': [address.to_dict(only=['id', 'text', 'send_time', 'receiver', 'sender'])
                                     for address in addresses]})

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        address = Address()
        address.text = args['text']
        address.sender = args['sender']
        address.receiver = args['receiver']
        address.send_time = datetime.datetime.now()

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
