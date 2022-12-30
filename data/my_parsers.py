import datetime

from flask_restful import reqparse


class ApiKeyParser(reqparse.RequestParser):
    def __init__(self):
        super().__init__()
        self.add_argument('apiKey', required=True)


class AuthParser(reqparse.RequestParser):
    def __init__(self):
        super().__init__()
        self.add_argument('phone', required=True)
        self.add_argument('session_id', required=True)
        self.add_argument('apiKey', required=True)


class EventParser(reqparse.RequestParser):
    def __init__(self):
        super().__init__()
        self.add_argument('name', required=True)
        self.add_argument('address', required=True)
        self.add_argument('datetime', type=str, required=True)
        self.add_argument('category_root_chain', required=True)
