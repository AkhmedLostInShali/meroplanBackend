import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Retailer(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'retailers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    products = orm.relationship("Product", back_populates='retailer')
    image_path = sqlalchemy.Column(sqlalchemy.String(128), nullable=True)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    owner = orm.relationship("User", foreign_keys='Retailer.owner_id', backref="retailer")
    address_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("addresses.id"))
    address = orm.relationship("Address")
    category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("categories.id"))
    category = orm.relationship("Category")