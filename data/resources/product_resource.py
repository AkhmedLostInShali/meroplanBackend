import datetime

from flask import jsonify, request
from flask_restful import abort, Resource
from sqlalchemy import func

from .. import db_session, my_parsers
from ..categories import Category
from ..products import Product
import logging

from ..retailers import Retailer
from ..users import User

logging.basicConfig(level=logging.INFO)

parser = my_parsers.ProductParser()


def abort_if_product_not_found(products_id):
    session = db_session.create_session()
    product = session.query(Product).get(products_id)
    if not product:
        abort(404, message=f"Product with id={products_id} not found")


class ProductsResource(Resource):
    def get(self, products_id):
        abort_if_product_not_found(products_id)
        db_sess = db_session.create_session()
        product = db_sess.query(Product).get(products_id)
        out_dict = product.to_dict(only=('id', 'image_path', 'name', 'search_info', 'description', 'price', 'quantity',
                                         'category', 'retailers_id'))
        out_dict['retailer'] = product.retailer.to_dict(only=('id', 'name', 'image_path'))
        db_sess.close()
        return jsonify({'product': out_dict})

    def delete(self, products_id):
        abort_if_product_not_found(products_id)
        db_sess = db_session.create_session()
        product = db_sess.query(Product).get(products_id)
        db_sess.delete(product)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})

    def put(self, products_id):
        abort_if_product_not_found(products_id)
        if not request.json:
            return jsonify({'error': 'Empty request'})
        db_sess = db_session.create_session()
        if request.json.get('id') and request.json.get('id') in [product.id for product
                                                                 in db_sess.query(Product).all()]:
            db_sess.close()
            return jsonify({'error': 'Id already exists'})
        product = db_sess.query(Product).get(products_id)
        product.id = request.json['id'] if request.json.get('id') else product.id
        product.name = request.json['name'] if request.json.get('name') else product.name
        product.image_path = request.json['image_path'] if request.json.get('image_path') else product.image_path
        product.price = request.json['price'] if request.json.get('price') else product.price
        product.quantity = request.json['quantity'] if request.json.get('quantity') else product.quantity
        product.category = request.json['category'] if request.json.get('category') else product.category
        product.description = request.json['description'] if request.json.get('description')\
            else product.description
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})


class ProductsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        products = db_sess.query(Product).all()
        out_list = []
        for product in products:
            out_dict = product.to_dict(only=('id', 'image_path', 'name', 'price', 'quantity', 'description',
                                             'search_info', 'retailers_id'))
            out_dict['retailers_name'] = db_sess.query(Retailer).get(product.retailers_id).name
            out_dict['categories'] = [int(x) for x in db_sess.query(Category).get(product.category_id
                                                                                  ).root_chain.split(';')]
            out_list.append(out_dict)
        db_sess.close()
        return jsonify(out_list)

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        if request.json.get('id') and request.json.get('id') in [user.id for user in db_sess.query(Product).all()]:
            db_sess.close()
            return jsonify({'error': 'Id already exists'})

        product = Product()
        if args.get('id'):
            product.id = args.get('id')
        product.name = args['name']
        product.image_path = args['image_path']
        product.description = args['description']
        product.name = args['price']
        product.image_path = args['category']
        product.description = args['quantity']
        product.search_info = ";".join([args['name'], args['description']]).lower()
        product.retailers_id = args['retailers_id']

        db_sess.add(product)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})


class ProductsSearchResource(Resource):
    def get(self, to_find, quantity):
        db_sess = db_session.create_session()
        category, keywords = to_find.split(';')[0], to_find.split(';')[1:]
        search_like = f"%{'%'.join(to_find.split())}%".lower()
        products = db_sess.query(Product).filter(Product.category == category
                                                 ).filter(Product.name.like(search_like) |
                                                          Product.description.like(search_like)
                                                          ).order_by(func.random()).limit(quantity).all()
        db_sess.close()
        return jsonify([product.to_dict(only=('id', 'image_path', 'name', 'price', 'category', 'quantity', 'description'
                                              , 'search_info', 'retailers_id')) for product in products])


class ProductsByCategoryResource(Resource):
    def get(self, category_id):
        db_sess = db_session.create_session()
        products = db_sess.query(Product).filter(
            Product.category_id == category_id |
            category_id in db_sess.query(Category).get(Product.category_id).root_chain.split(';')).all()
        out_list = []
        for product in products:
            out_dict = product.to_dict(only=('id', 'image_path', 'name', 'price', 'quantity', 'description',
                                             'search_info', 'retailers_id'))
            out_dict['retailers_name'] = db_sess.query(Retailer).get(product.retailers_id).name
            out_dict['categories'] = [int(x) for x in db_sess.query(Category).get(product.category_id
                                                                                  ).root_chain.split(';')]
            out_list.append(out_dict)
        db_sess.close()
        return jsonify(out_list)

    def post(self):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        if request.json.get('id') and request.json.get('id') in [user.id for user in db_sess.query(Product).all()]:
            db_sess.close()
            return jsonify({'error': 'Id already exists'})

        product = Product()
        if args.get('id'):
            product.id = args.get('id')
        product.name = args['name']
        product.image_path = args['image_path']
        product.description = args['description']
        product.name = args['price']
        product.image_path = args['category']
        product.description = args['quantity']
        product.search_info = ";".join([args['name'], args['description']]).lower()
        product.retailers_id = args['retailers_id']

        db_sess.add(product)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})


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
