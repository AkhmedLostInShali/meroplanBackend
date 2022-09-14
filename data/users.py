import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


class Association(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "association"
    buyer_id = sqlalchemy.Column('buyer_id', sqlalchemy.String(8), sqlalchemy.ForeignKey('users.id'),
                                 index=True, primary_key=True)
    products_id = sqlalchemy.Column('products_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('products.id'), index=True,
                                    primary_key=True)
    quantity = sqlalchemy.Column('quantity', sqlalchemy.Integer, default=1)
    product = orm.relation("Product", lazy="joined")


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.String(8),
                           primary_key=True, unique=True)
    phone = sqlalchemy.Column(sqlalchemy.String(32), index=True, unique=True, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String(64), nullable=True)
    rank = sqlalchemy.Column(sqlalchemy.String(32), default='consumer')
    image_path = sqlalchemy.Column(sqlalchemy.String(128), default='static/img/users/default.png')
    secret = sqlalchemy.Column(sqlalchemy.String(256), nullable=False)
    cart = orm.relation('Association', cascade="all, delete-orphan", lazy="joined")
    address_list = orm.relationship("Address", back_populates='owner')

    def set_secret(self, secret):
        self.secret = generate_password_hash(secret)

    def check_secret(self, secret):
        return check_password_hash(self.secret, secret)
