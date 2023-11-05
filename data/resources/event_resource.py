import datetime
import os
import random
import string

from PIL import Image
from flask import jsonify, request
from flask_restful import abort, Resource
from werkzeug.utils import secure_filename

import image_cutter
from server import token_required, allowed_file
from .abort_if_not_found import abort_if_event_not_found, abort_if_user_not_found
from .. import db_session, my_parsers
from ..events import Event
import logging

from ..users import User

logging.basicConfig(level=logging.INFO)

parser = my_parsers.EventParser()


class EventsResource(Resource):
    def get(self, events_id):
        abort_if_event_not_found(events_id)
        db_sess = db_session.create_session()
        event = db_sess.query(Event).get(events_id)
        out_dict = event.to_dict(only=('id', 'image_path', 'name', 'search_info', 'address'))
        out_dict['sponsors_name'] = event.sponsor.name  # тут я упростил
        out_dict['sponsors_image_path'] = event.sponsor.image_path
        out_dict['date'] = event.datetime.strftime('%m.%d.%Y')
        out_dict['time'] = event.datetime.strftime('%H:%M')
        out_dict['categories'] = [int(x) for x in event.category_root_chain.split(';') if x]
        db_sess.close()
        return jsonify({'item': out_dict, 'status_code': 200})

    def delete(self, events_id):
        abort_if_event_not_found(events_id)
        db_sess = db_session.create_session()
        product = db_sess.query(Event).get(events_id)
        db_sess.delete(product)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})

    # def put(self, events_id):
    #     abort_if_event_not_found(events_id)
    #     if not request.json:
    #         return jsonify({'error': 'Empty request'})
    #     db_sess = db_session.create_session()
    #     if request.json.get('id') and request.json.get('id') in [product.id for product
    #                                                              in db_sess.query(Event).all()]:
    #         db_sess.close()
    #         return jsonify({'error': 'Id already exists'})
    #     product = db_sess.query(Event).get(events_id)
    #     product.id = request.json['id'] if request.json.get('id') else product.id
    #     product.name = request.json['name'] if request.json.get('name') else product.name
    #     product.image_path = request.json['image_path'] if request.json.get('image_path') else product.image_path
    #     product.price = request.json['price'] if request.json.get('price') else product.price
    #     product.quantity = request.json['quantity'] if request.json.get('quantity') else product.quantity
    #     product.category = request.json['category'] if request.json.get('category') else product.category
    #     product.description = request.json['description'] if request.json.get('description')\
    #         else product.description
    #     db_sess.commit()
    #     db_sess.close()
    #     return jsonify({'success': 'OK'})


class EventsListResource(Resource):
    @token_required
    def get(self, token_data):
        users_id = token_data['user_id']
        abort_if_user_not_found(users_id)

        db_sess = db_session.create_session()

        advanced_filter = request.args.get('advanced_filter', default=None, type=str) == 'yes'

        search_query = f"%{'%'.join(request.args.get('search_query', default='', type=str).split('_'))}%".lower()
        if advanced_filter:
            events_query = db_sess.query(Event).filter(
                    Event.datetime > datetime.datetime.now()).filter(
                    Event.search_info.ilike(search_query))
            category_af = request.args.get('category', default=None, type=str)
            first_date_af = request.args.get('first_date', default=None, type=str)
            last_date_af = request.args.get('last_date', default=None, type=str)
            min_member_af = request.args.get('min_member', default=None, type=str)
            max_member_af = request.args.get('max_member', default=None, type=str)
            address_af = request.args.get('address', default=None, type=str)
            # sorting_af = request.args.get('sorting', default='basic', type=str)
            if category_af:
                events_query = events_query.filter(Event.category_id == int(category_af))
            if first_date_af:
                events_query = events_query.filter(Event.datetime >= datetime.datetime.strptime(
                    first_date_af, '%d.%m.%y').replace(hour=23, minute=59))
            if last_date_af:
                events_query = events_query.filter(Event.datetime <= datetime.datetime.strptime(
                    last_date_af, '%d.%m.%y').replace(hour=23, minute=59))
            if min_member_af:
                events_query = events_query.filter(Event.member_capacity >= int(min_member_af))
            if max_member_af:
                events_query = events_query.filter(Event.member_capacity <= int(max_member_af))
            if address_af:
                events_query = events_query.filter(Event.search_info.ilike(f'%{address_af.lower()}%'))
            # if sorting_af == 'basic':
            #     events_query = events_query.order_by(Event.votes.desc())
        else:
            categories = db_sess.query(User).get(users_id).favorite_categories

            if categories:
                events_query = db_sess.query(Event).filter(
                    Event.datetime > datetime.datetime.now()).order_by(Event.datetime.desc()).filter(
                    Event.category_id.in_(categories.split(';'))).filter(
                    Event.search_info.ilike(search_query))
            else:
                events_query = db_sess.query(Event).filter(
                    Event.datetime > datetime.datetime.now()).order_by(Event.datetime.desc()).filter(
                    Event.search_info.ilike(search_query))

        if events_query.count() == 0:
            db_sess.close()
            return jsonify({'items': [], 'total_pages': 0, 'status_code': 404})

        page_len = 10
        total_pages = events_query.count() // page_len + (1 if events_query.count() % page_len else 0)
        page = min([total_pages, request.args.get('page', default=1, type=int)])
        events = events_query.slice((page - 1) * page_len, page * page_len).all()

        current_user_id = token_data['user_id']

        out_list = []
        for event in events:
            out_dict = event.to_dict(only=('id', 'image_path', 'name', 'address'))
            out_dict['members'] = len(event.members)
            out_dict['is_membered'] = current_user_id in [assoc.member_id for assoc in event.members]
            out_dict['sponsors_id'] = event.sponsor.id
            out_dict['sponsors_name'] = ' '.join([event.sponsor.name, (event.sponsor.surname if
                                                                       event.sponsor.surname else '')])  # тут я упростил
            out_dict['sponsors_image_path'] = event.sponsor.image_path
            out_dict['date'] = event.datetime.strftime('%d.%m.%Y')
            out_dict['time'] = event.datetime.strftime('%H:%M')
            out_dict['category_id'] = event.category_id
            out_list.append(out_dict)
        db_sess.close()
        # print("got here")
        print(out_list)
        return jsonify({'items': out_list, 'total_pages': total_pages, 'status_code': 200})\


    @token_required
    def post(self, token_data):
        db_sess = db_session.create_session()
        event = Event()
        rand_id = ''.join(random.choices(string.digits + string.ascii_letters + '-_', k=8))
        while rand_id in db_sess.query(Event.id).all():
            rand_id = ''.join(random.choices(string.digits + string.ascii_letters + '-_', k=8))
        event.id = rand_id
        file_code = secure_filename(f'{str(rand_id) + "-" + str(token_data["user_id"])}.png')
        filepath = f'static/img/events/{file_code}'
        if os.path.exists(filepath):
            os.remove(filepath)
        file = request.files['file']
        logging.info(filepath)
        if file and allowed_file(file.filename):
            file.save(filepath)
            logging.info(image_cutter.get_central_rect((328, 190), filepath))
        else:
            db_sess.close()
            return abort(404)

        event.image_path = filepath

        # args = parser.parse_args()

        # event.name = args['name']
        # event.datetime = datetime.datetime.fromisoformat(args['datetime'])
        # event.category_root_chain = args['category_root_chain']
        # event.address = args['address']
        # event.search_info = ";".join([args['name'], args['description'], args['address']]).lower()
        # event.sponsors_id = token_data['user_id']

        event.name = request.args.get('name')
        event.datetime = datetime.datetime.fromisoformat(request.args.get('datetime'))

        event.category_root_chain = request.args.get('category_root_chain')
        event.address = request.args.get('address')
        event.search_info = ";".join([request.args.get('name'), request.args.get('address')]).lower()
        event.sponsors_id = token_data['user_id']

        db_sess.add(event)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})