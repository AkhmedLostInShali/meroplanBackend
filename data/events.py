import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Event(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'events'

    id = sqlalchemy.Column(sqlalchemy.String(8),
                           primary_key=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String(256), nullable=True)
    search_info = sqlalchemy.Column(sqlalchemy.String(256), nullable=True)
    image_path = sqlalchemy.Column(sqlalchemy.String(128), nullable=False)
    datetime = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    address = sqlalchemy.Column(sqlalchemy.String(256), nullable=False)
    gender = sqlalchemy.Column(sqlalchemy.String(16), default='uni', nullable=False)
    member_capacity = sqlalchemy.Column(sqlalchemy.Integer, default=100, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)
    sponsors_id = sqlalchemy.Column(sqlalchemy.String(8), sqlalchemy.ForeignKey("users.id"))
    sponsor = orm.relationship("User", backref='sponsored_events')
    category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("categories.id"))
    # category_root_chain = sqlalchemy.Column(sqlalchemy.String(128), sqlalchemy.ForeignKey("categories.root_chain"),
    #                                         default='1', nullable=False, index=True)
    category = orm.relationship("Category")
