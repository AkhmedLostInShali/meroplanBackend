import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Category(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'categories'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    root_chain = sqlalchemy.Column(sqlalchemy.String(128), nullable=False, default='1', unique=True)
    parents_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    image_path = sqlalchemy.Column(sqlalchemy.String(128), nullable=False)
    main_color_argb = sqlalchemy.Column(sqlalchemy.String(8), default='aaff5602')
    secondary_color_argb = sqlalchemy.Column(sqlalchemy.String(8), default='aa02abff')
    name = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)