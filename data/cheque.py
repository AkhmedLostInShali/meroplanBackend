import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Cheque(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'cheques'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    list_of_products = sqlalchemy.Column(sqlalchemy.String(256), nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    order_time = sqlalchemy.Column(sqlalchemy.Time, nullable=True)
    buyers_name = sqlalchemy.Column(sqlalchemy.String(64), nullable=True)
    buyers_phone = sqlalchemy.Column(sqlalchemy.String(32), nullable=True)
    buyers_address = sqlalchemy.Column(sqlalchemy.String(512), nullable=False)
    full_cheque = sqlalchemy.Column(sqlalchemy.String(1024), nullable=False)