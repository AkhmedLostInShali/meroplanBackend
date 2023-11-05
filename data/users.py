import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


subscribes = sqlalchemy.Table('subscribes', SqlAlchemyBase.metadata,
                              sqlalchemy.Column('subscriber_id', sqlalchemy.String(8), sqlalchemy.ForeignKey('users.id'),
                                                index=True),
                              sqlalchemy.Column('subscribed_id', sqlalchemy.String(8), sqlalchemy.ForeignKey('users.id'),
                                                index=True))


class MemberAssociation(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "member_association"
    member_id = sqlalchemy.Column('member_id', sqlalchemy.String(8), sqlalchemy.ForeignKey('users.id'), index=True,
                                  primary_key=True)
    events_id = sqlalchemy.Column('events_id', sqlalchemy.String(8), sqlalchemy.ForeignKey('events.id'), index=True,
                                  primary_key=True)
    event = orm.relation("Event", backref="members", lazy="joined")


class VoteAssociation(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "vote_association"
    member_id = sqlalchemy.Column('user_id', sqlalchemy.String(8), sqlalchemy.ForeignKey('users.id'), index=True,
                                  primary_key=True)
    events_id = sqlalchemy.Column('event_id', sqlalchemy.String(8), sqlalchemy.ForeignKey('events.id'), index=True,
                                  primary_key=True)
    vote_text = sqlalchemy.Column(sqlalchemy.String(256), nullable=True)
    event = orm.relation("Event", backref="votes", lazy="joined")


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.String(8),
                           primary_key=True, unique=True)
    phone = sqlalchemy.Column(sqlalchemy.String(32), index=True, unique=True, nullable=True)
    nickname = sqlalchemy.Column(sqlalchemy.String(64), nullable=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String(64), nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String(64), nullable=True)
    image_path = sqlalchemy.Column(sqlalchemy.String(128), default='static/img/users/default.png')
    secret = sqlalchemy.Column(sqlalchemy.String(256), nullable=False)
    favorite_categories = sqlalchemy.Column(sqlalchemy.String(16), nullable=True)
    membered_events = orm.relation('MemberAssociation', cascade="all, delete-orphan", lazy="joined")

    voted_events = orm.relation('VoteAssociation', cascade="all, delete-orphan", lazy="joined")

    subscribed = orm.relation('User', secondary=subscribes,
                              primaryjoin=(subscribes.c.subscriber_id == id),
                              secondaryjoin=(subscribes.c.subscribed_id == id),
                              backref='subscribes',
                              lazy='dynamic')

    def set_secret(self, secret):
        self.secret = generate_password_hash(secret)

    def check_secret(self, secret):
        return check_password_hash(self.secret, secret)

    def to_member(self, event):
        if event.id not in [assoc.events_id for assoc in self.membered_events]:
            assoc = MemberAssociation()
            assoc.event = event
            self.membered_events.append(assoc)
            return self

    def to_dismember(self, event):
        if event.id in [assoc.events_id for assoc in self.membered_events]:
            self.membered_events.remove([assoc for assoc in self.membered_events if assoc.events_id == event.id][0])
            return self

    def to_vote(self, event):
        if event.id not in [assoc.events_id for assoc in self.membered_events]:
            assoc = VoteAssociation()
            assoc.event = event
            self.voted_events.append(assoc)
            return self

    def to_unvote(self, event):
        if event.id in [assoc.events_id for assoc in self.voted_events]:
            self.voted_events.remove([assoc for assoc in self.voted_events if assoc.events_id == event.id][0])
            return self

    def to_subscribe(self, user):
        if not self.is_subscribed(user):
            self.subscribed.append(user)
            return self

    def to_unsubscribe(self, user):
        if self.is_subscribed(user):
            self.subscribed.remove(user)
            return self

    def is_subscriber(self, user):
        return self.subscribed.filter_by(nickname=user.nickname).count() > 0

    def is_subscribed(self, user):
        return self.subscribed.filter(subscribes.c.subscribed_id == user.id).count() > 0
