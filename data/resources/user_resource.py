import datetime

from flask import jsonify, request
from flask_restful import abort, Resource

from .event_resource import abort_if_event_not_found
from .. import db_session
from ..events import Event
from ..users import User
from server import token_required
import logging

logging.basicConfig(level=logging.INFO)


def abort_if_user_not_found(users_id):
    session = db_session.create_session()
    user = session.query(User).get(users_id)
    if not user:
        abort(404, message=f"User {users_id} not found")
    session.close()


def jsonify_user(user):
    user_dict = user.to_dict(only=['id', 'nickname', 'name', 'surname', 'phone', 'image_path'])
    return user_dict


class MyProfileResource(Resource):
    @token_required
    def get(self, token_data):
        users_id = token_data['user_id']
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(users_id)
        user_dict = jsonify_user(user)
        upcoming_events = []
        visited_events = []
        for event in user.membered_events:
            out_dict = event.to_dict(only=('id', 'image_path', 'name', 'address'))
            out_dict['members'] = event.members.count()
            out_dict['sponsors_name'] = event.sponsor.name  # тут я упростил
            out_dict['sponsors_image_path'] = event.sponsor.image_path
            out_dict['date'] = event.datetime.strftime('%m.%d.%Y')
            out_dict['time'] = event.datetime.strftime('%H:%M')
            if event.datetime > datetime.datetime.now():
                upcoming_events.append(out_dict)
            else:
                visited_events.append(out_dict)
        user_dict['upcoming_events'] = upcoming_events
        user_dict['visited_events'] = visited_events
        sponsored_events = []
        for event in user.sponsored_events:
            out_dict = event.to_dict(only=('id', 'image_path', 'name', 'address'))
            out_dict['members'] = event.members.count()
            out_dict['date'] = event.datetime.strftime('%m.%d.%Y')
            out_dict['time'] = event.datetime.strftime('%H:%M')
            sponsored_events.append(out_dict)
        user_dict['sponsored_events'] = visited_events
        db_sess.close()
        return jsonify({'item': user_dict, 'status_code': 200})

    @token_required
    def delete(self, token_data):
        users_id = token_data['user_id']
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(users_id)
        if users_id < 3:
            return jsonify({'error': "you can't delete moderation"})
        db_sess.delete(user)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})

    @token_required
    def put(self, token_data):
        if not request.args:
            return jsonify({'error': 'Empty request'})
        users_id = token_data['user_id']
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(users_id)
        name = request.args['name'] if request.args.get('name') else user.name
        user.name = name
        surname = request.args['surname'] if request.args.get('surname') else user.surname
        user.surname = surname
        db_sess.commit()
        db_sess.close()
        return jsonify({'status_code': '200'})


class UsersResource(Resource):
    @token_required
    def get(self, users_id, token_data):
        current_users_id = token_data['user_id']
        abort_if_user_not_found(current_users_id)
        db_sess = db_session.create_session()
        current_user = db_sess.query(User).get(current_users_id)
        user = db_sess.query(User).get(users_id)
        user_dict = jsonify_user(user)
        if current_user in user.subscribed:
            if user in current_user.subscribed:
                friend_state = 'friend'
            else:
                friend_state = 'subscribed'
        elif user in current_user.subscribed:
            friend_state = 'subscribes'
        else:
            friend_state = 'none'
        user_dict['is_friend'] = friend_state
        db_sess.close()
        return jsonify({'item': user_dict, 'status_code': 200})


class SubscribeResource(Resource):
    @token_required
    def get(self, token_data, *args):
        users_id = token_data['user_id']
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(users_id)
        out_list = []
        for sub in user.subscribes:
            if sub in user.subscribed:
                events = []
                for event in sub.sponsored_events:
                    if event.datetime > datetime.datetime.now():
                        event_dict = event.to_dict(only=('id', 'image_path', 'name', 'address'))
                        event_dict['members'] = event.members.count()
                        event_dict['date'] = event.datetime.strftime('%m.%d.%Y')
                        event_dict['time'] = event.datetime.strftime('%H:%M')
                        events.append(event_dict)
                out_dict = {
                    'friend': sub.to_dict(only=['id', 'name', 'surname', 'image_path']),
                    'events': events
                }
                out_list.append(out_dict)
        return jsonify({'items': out_list, 'status_code': 200})

    @token_required
    def put(self, users_id, token_data):
        current_users_id = token_data['user_id']
        abort_if_user_not_found(current_users_id)
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        subscriber = db_sess.query(User).get(current_users_id)
        user = db_sess.query(User).get(users_id)
        user.subscribed.append(subscriber)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})

    @token_required
    def delete(self, users_id, token_data):
        current_users_id = token_data['user_id']
        abort_if_user_not_found(current_users_id)
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        subscriber = db_sess.query(User).get(current_users_id)
        user = db_sess.query(User).get(users_id)
        user.subscribed.remove(subscriber)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})


class MemberResource(Resource):
    @token_required
    def put(self, events_id, token_data):
        current_users_id = token_data['user_id']
        abort_if_user_not_found(current_users_id)
        abort_if_event_not_found(events_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_users_id)
        event = db_sess.query(Event).get(events_id)
        user.to_member(event)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})

    @token_required
    def delete(self, events_id, token_data):
        current_users_id = token_data['user_id']
        abort_if_user_not_found(current_users_id)
        abort_if_event_not_found(events_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_users_id)
        event = db_sess.query(Event).get(events_id)
        user.to_dismember(event)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})
