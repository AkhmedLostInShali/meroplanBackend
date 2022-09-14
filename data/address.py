import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Address(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'addresses'

    id = sqlalchemy.Column(sqlalchemy.String(8),
                           primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    city = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    street = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    house = sqlalchemy.Column(sqlalchemy.String(32), nullable=False)
    flat = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    entrance = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    level = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    comment = sqlalchemy.Column(sqlalchemy.String(128), nullable=True)
    owner_id = sqlalchemy.Column(sqlalchemy.String(8), sqlalchemy.ForeignKey("users.id"), nullable=False)
    owner = orm.relationship("User", back_populates='address_list')
