from flask import jsonify, request
from flask_restful import abort, Resource
from sqlalchemy import and_
from .. import db_session, my_parsers
from ..retailers import Retailer
import logging
import datetime

logging.basicConfig(level=logging.INFO)

parser = my_parsers.RetailerParser()


def abort_if_retailer_not_found(retailer_id):
    session = db_session.create_session()
    retailer = session.query(Retailer).get(retailer_id)
    if not retailer:
        abort(404, message=f"Retailer {retailer_id} not found")


class RetailersResource(Resource):
    def get(self, retailer_id):
        abort_if_retailer_not_found(retailer_id)
        db_sess = db_session.create_session()
        retailer = db_sess.query(Retailer).get(retailer_id)
        out_dict = retailer.to_dict(only=('id', 'name', 'image_path', 'category', 'owner_id', 'products', 'address_id'))
        return jsonify({'retailer': out_dict})

    def delete(self, retailer_id):
        abort_if_retailer_not_found(retailer_id)
        db_sess = db_session.create_session()
        retailer = db_sess.query(Retailer).get(retailer_id)
        if retailer_id < 3:
            return jsonify({'error': "you can't delete moderation"})
        db_sess.delete(retailer)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def put(self, retailer_id):
        abort_if_retailer_not_found(retailer_id)
        if not request.json:
            return jsonify({'error': 'Empty request'})
        db_sess = db_session.create_session()
        retailer = db_sess.query(Retailer).get(retailer_id)
        retailer.name = request.json['name'] if request.json.get('name') else retailer.name
        retailer.category = request.json['category'] if request.json.get('category') else retailer.category
        db_sess.commit()
        return jsonify({'success': 'OK'})


class RetailersListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()

        category_id = request.args.get('category_id', default=0, type=int)
        if category_id:
            retailers_query = db_sess.query(Retailer).filter(
                Retailer.category_root_chain.startswith(f'{category_id};') |
                Retailer.category_root_chain.endswith(f';{category_id}') |
                Retailer.category_root_chain.contains(f';{category_id};'))
        else:
            retailers_query = db_sess.query(Retailer)

        if retailers_query.count() == 0:
            return jsonify({'items': [], 'total_pages': 0, 'status_code': 200})

        page_len = 5
        total_pages = retailers_query.count() // page_len + (1 if retailers_query.count() % page_len else 0)
        page = min([total_pages, max(1, request.args.get('page', default=1, type=int))])
        retailers = retailers_query.slice((page - 1) * page_len, page * page_len).all()

        out_list = []
        for retailer in retailers:
            out_dict = retailer.to_dict(only=('id', 'image_path', 'name'))
            out_dict['categories'] = [int(x) for x in retailer.category_root_chain.split(';') if x]
            out_list.append(out_dict)
        db_sess.close()
        return jsonify({'items': out_list, 'total_pages': total_pages, 'status_code': 200})

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        retailer = Retailer()
        retailer.name = args['name']
        retailer.category = args['category']
        retailer.image_path = args['image_path']
        retailer.owner_id = args['owner_id']
        retailer.address_id = args['address_id']

        db_sess.add(retailer)
        db_sess.commit()
        return jsonify({'success': 'OK'})


# class MessagesDialogResource(Resource):
#     def get(self, sender, receiver):
#         db_sess = db_session.create_session()
#         logging.info(str(sender) + '-' + str(receiver))
#         messages = db_sess.query(Message).filter(and_(Message.sender_id == sender, Message.receiver_id == receiver) |
#                                                  and_(Message.sender_id == receiver, Message.receiver_id == sender)
#                                                  ).all()
#         return jsonify({'messages': [message.to_dict(only=['id', 'text', 'send_time', 'receiver_id', 'sender_id'])
#                                      for message in messages]})
