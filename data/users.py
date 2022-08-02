import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


class Association(SqlAlchemyBase):
    __tablename__ = "association"
    buyer_id = sqlalchemy.Column('buyer_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'),
                                 index=True, primary_key=True)
    products_id = sqlalchemy.Column('products_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('products.id'), index=True,
                                    primary_key=True)
    quantity = sqlalchemy.Column('quantity', sqlalchemy.Integer, default=1)
    product = orm.relation("Product", lazy="joined")


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    phone = sqlalchemy.Column(sqlalchemy.String(32), index=True, unique=True, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String(64), nullable=True)
    rank = sqlalchemy.Column(sqlalchemy.String(32), default='consumer')
    korzina = orm.relation('Association', cascade="all, delete-orphan", lazy="joined")
    address_list = orm.relationship("Address", back_populates='owner')
