import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Retailer(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'retailers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    search_info = sqlalchemy.Column(sqlalchemy.String(256), nullable=True)
    products = orm.relationship("Product", back_populates='retailer')
    image_path = sqlalchemy.Column(sqlalchemy.String(128), nullable=True)
    owner_id = sqlalchemy.Column(sqlalchemy.String(8), sqlalchemy.ForeignKey("users.id"), nullable=False)
    owner = orm.relationship("User", foreign_keys='Retailer.owner_id', backref="retailer")
    address_id = sqlalchemy.Column(sqlalchemy.String(8), sqlalchemy.ForeignKey("addresses.id"), nullable=False)
    address = orm.relationship("Address")
    category_root_chain = sqlalchemy.Column(sqlalchemy.String(128), sqlalchemy.ForeignKey("categories.root_chain")
                                            , default='1', nullable=False, index=True)
    category = orm.relationship("Category")