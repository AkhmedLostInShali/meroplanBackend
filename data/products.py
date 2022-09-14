import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Product(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String(256), nullable=False)
    search_info = sqlalchemy.Column(sqlalchemy.String(256), nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    image_path = sqlalchemy.Column(sqlalchemy.String(128), nullable=False)
    retailers_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("retailers.id"))
    retailer = orm.relationship("Retailer", back_populates='products')
    category_root_chain = sqlalchemy.Column(sqlalchemy.String(128), sqlalchemy.ForeignKey("categories.root_chain")
                                            , default='1', nullable=False, index=True)
    category = orm.relationship("Category")
