from flask_restful import abort

from data import db_session
from data.events import Event
from data.users import User


def abort_if_user_not_found(users_id):
    session = db_session.create_session()
    user = session.query(User).get(users_id)
    if not user:
        abort(404, message=f"User {users_id} not found")
    session.close()


def abort_if_event_not_found(events_id):
    session = db_session.create_session()
    event = session.query(Event).get(events_id)
    if not event:
        abort(404, message=f"Event with id={events_id} not found")