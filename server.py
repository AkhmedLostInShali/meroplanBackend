from flask import Flask
from flask_restful import Api
from data import db_session
from werkzeug.serving import WSGIRequestHandler

from data.resources import product_resource, category_resource

import logging

logging.basicConfig(level=logging.WARNING)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
path = 'https://localhost:8080'
api = Api(app)


def main():
    db_session.global_init('Akhmed', 'Akhmedik2005', 'localhost:3306', "took")
    # api.add_resource(user_resource.UsersResource, '/api/users/<int:users_id>')
    # api.add_resource(user_resource.UsersSearchResource, '/api/users/<to_find>')
    # api.add_resource(user_resource.UsersListResource, '/api/users')
    #
    # api.add_resource(user_resource.UsersSubscriptionsResource, '/api/subscribe/<from_for>/<int:users_id>')
    # api.add_resource(user_resource.UsersSubscribeResource, '/api/subscribe/<int:users_id>/<int:subscribers_id>')

    api.add_resource(product_resource.ProductsResource, '/api/products/<int:products_id>')
    # api.add_resource(product_resource.ProductsSearchResource, '/api/products/<to_find>')
    api.add_resource(product_resource.ProductsListResource, '/api/products')
    api.add_resource(product_resource.ProductsByCategoryResource, '/api/products_by_category/<int:category_id>')

    api.add_resource(category_resource.CategoriesListResource, '/api/categories')
    #
    # api.add_resource(message_resource.MessagesResource, '/api/messages/<int:message_id>')
    # api.add_resource(message_resource.MessagesListResource, '/api/messages')
    # api.add_resource(message_resource.MessagesDialogResource, '/api/messages/<int:sender>/<int:receiver>')
    #
    # api.add_resource(comment_resource.CommentsResource, '/api/comments/<int:comment_id>')
    # api.add_resource(comment_resource.CommentsListResource, '/api/comments')
    # api.add_resource(comment_resource.CommentsTreeResource, '/api/comments_tree/<int:publications_id>')
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()