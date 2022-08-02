import datetime

from flask_restful import reqparse


class ProductParser(reqparse.RequestParser):
    def __init__(self):
        super().__init__()
        self.add_argument('id', required=False, type=int)
        self.add_argument('name', required=True)
        self.add_argument('price', required=True, type=int)
        self.add_argument('description', required=True)
        self.add_argument('quantity', type=int, required=True)
        self.add_argument('image_path', required=True)
        self.add_argument('category', required=False)
        self.add_argument('retailers_id', required=False)


class UserParser(reqparse.RequestParser):
    def __init__(self):
        super().__init__()
        self.add_argument('id', required=False, type=int)
        self.add_argument('phone', required=True)
        self.add_argument('name', required=False)
        self.add_argument('rank', required=False)


class RetailerParser(reqparse.RequestParser):
    def __init__(self):
        super().__init__()
        self.add_argument('id', required=False, type=int)
        self.add_argument('name', required=True)
        self.add_argument('image_path', required=True)
        self.add_argument('category', required=False)
        self.add_argument('owner_id', required=False)
        self.add_argument('address_id', required=False)


class AddressParser(reqparse.RequestParser):
    def __init__(self):
        super().__init__()
        self.add_argument('id', required=False, type=int)
        self.add_argument('name', required=True)
        self.add_argument('city', required=True)
        self.add_argument('street', required=True)
        self.add_argument('house', required=True)
        self.add_argument('flat', required=False, type=int)
        self.add_argument('entrance', required=False, type=int)
        self.add_argument('level', required=False, type=int)
        self.add_argument('comment', required=False)
        self.add_argument('owner_id', required=True, type=int)
