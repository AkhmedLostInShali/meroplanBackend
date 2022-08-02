import datetime

from flask import jsonify, request
from flask_restful import abort, Resource
from sqlalchemy import func

from .. import db_session, my_parsers
from ..categories import Category
import logging

logging.basicConfig(level=logging.INFO)

parser = my_parsers.ProductParser()


def abort_if_category_not_found(category_id):
    session = db_session.create_session()
    category = session.query(Category).get(category_id)
    if not category:
        abort(404, message=f"Category with id={category_id} not found")


class CategoriesResource(Resource):
    def get(self, category_id):
        abort_if_category_not_found(category_id)
        db_sess = db_session.create_session()
        category = db_sess.query(Category).get(category_id)
        out_dict = category.to_dict(only=('id', 'image_path', 'name', 'search_info', 'description', 'price', 'quantity',
                                          'category', 'retailers_id'))
        out_dict['retailer'] = category.retailer.to_dict(only=('id', 'name', 'image_path'))
        db_sess.close()
        return jsonify({'category': out_dict})

    def delete(self, category_id):
        abort_if_category_not_found(category_id)
        db_sess = db_session.create_session()
        category = db_sess.query(Category).get(category_id)
        db_sess.delete(category)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})

    def put(self, category_id):
        abort_if_category_not_found(category_id)
        if not request.json:
            return jsonify({'error': 'Empty request'})
        db_sess = db_session.create_session()
        if request.json.get('id') and request.json.get('id') in [category.id for category
                                                                 in db_sess.query(Category).all()]:
            db_sess.close()
            return jsonify({'error': 'Id already exists'})
        category = db_sess.query(Category).get(category_id)
        category.id = request.json['id'] if request.json.get('id') else category.id
        category.name = request.json['name'] if request.json.get('name') else category.name
        category.image_path = request.json['image_path'] if request.json.get('image_path') else category.image_path
        category.price = request.json['price'] if request.json.get('price') else category.price
        category.quantity = request.json['quantity'] if request.json.get('quantity') else category.quantity
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})


class CategoriesListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        categories = db_sess.query(Category).all()
        out_list = []
        for category in categories:
            out_dict = category.to_dict(only=('id', 'image_path', 'name', 'parents_id'))
            out_dict['root_chain'] = [int(x) for x in category.root_chain.split(';')]
            out_list.append(out_dict)
        db_sess.close()
        return jsonify(out_list)

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        if request.json.get('id') and request.json.get('id') in [user.id for user in db_sess.query(Category).all()]:
            db_sess.close()
            return jsonify({'error': 'Id already exists'})

        category = Category()
        if args.get('id'):
            category.id = args.get('id')
        category.name = args['name']
        category.image_path = args['image_path']
        category.description = args['description']
        category.name = args['price']
        category.image_path = args['category']
        category.description = args['quantity']
        category.search_info = ";".join([args['name'], args['description']]).lower()
        category.retailers_id = args['retailers_id']

        db_sess.add(category)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})


# class ProductsSearchResource(Resource):
#     def get(self, to_find, quantity):
#         db_sess = db_session.create_session()
#         category, keywords = to_find.split(';')[0], to_find.split(';')[1:]
#         search_like = f"%{'%'.join(to_find.split())}%".lower()
#         categories = db_sess.query(Category).filter(Category.category == category
#                                                  ).filter(Category.name.like(search_like) |
#                                                           Category.description.like(search_like)
#                                                           ).order_by(func.random()).limit(quantity).all()
#         return jsonify([category.to_dict(only=('id', 'image_path', 'name', 'price', 'category', 'quantity', 'description'
#                                               , 'search_info', 'retailers_id')) for category in categories])


# class PublicationsCheerResource(Resource):
#     def put(self, users_id, publications_id):
#         abort_if_user_not_found(users_id)
#         abort_if_product_not_found(publications_id)
#         db_sess = db_session.create_session()
#         user = db_sess.query(User).get(users_id)
#         publication = db_sess.query(Product).get(publications_id)
#         publication.cheers.append(user)
#         db_sess.commit()
#         return jsonify({'success': 'OK'})
#
#     def delete(self, users_id, publications_id):
#         abort_if_user_not_found(users_id)
#         abort_if_product_not_found(publications_id)
#         db_sess = db_session.create_session()
#         user = db_sess.query(User).get(users_id)
#         publication = db_sess.query(Product).get(publications_id)
#         publication.cheers.remove(user)
#         db_sess.commit()
#         return jsonify({'success': 'OK'})
