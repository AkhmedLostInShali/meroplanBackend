import datetime

from flask import jsonify, request
from flask_restful import abort, Resource
from sqlalchemy import null

from .. import db_session
from ..categories import Category
import logging

logging.basicConfig(level=logging.INFO)


def abort_if_category_not_found(category_id):
    session = db_session.create_session()
    category = session.query(Category).get(category_id)
    if not category:
        abort(404, message=f"Category with id={category_id} not found")


class CategoriesListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        parents_id = request.args.get('parents_id', default=0, type=int)
        if parents_id:
            categories_query = db_sess.query(Category).filter(
                Category.root_chain.startswith(f'{parents_id};') |
                Category.root_chain.contains(f';{parents_id};'))
        else:
            categories_query = db_sess.query(Category).filter(Category.parents_id == null())

        if categories_query.count() == 0:
            return jsonify({'items': [], 'status_code': 200})

        out_list = []

        for category in categories_query.all():
            out_dict = category.to_dict(only=('id', 'image_path', 'name', 'parents_id'))
            out_dict['root_chain'] = [int(x) for x in category.root_chain.split(';') if x]
            out_list.append(out_dict)
        db_sess.close()
        return jsonify({'items': out_list, 'status_code': 200})