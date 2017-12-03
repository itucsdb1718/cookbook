import psycopg2 as dbapi2

from .abstract import *
from hashlib import md5

from flask_login import UserMixin


class Users(Model, UserMixin):
    username = CharField(max_length=50, null=False)
    firstname = CharField(max_length=50, null=False, default='-')
    lastname = CharField(max_length=50, null=False)
    email = CharField(max_length=80, null=False)
    password = CharField(max_length=32, null=False)  # hash of password

    @staticmethod
    def create_hash(password):
        password = password.encode()

        a = md5(password).hexdigest()
        b = md5(password[::-1]).hexdigest()
        c = (a + b).encode()

        return md5(c).hexdigest()

    def set_password(self, password):
        self.password = Users.create_hash(password)

    def check_password(self, password):
        return Users.create_hash(password) == self.password

    def get_id(self):
        return self.id


class Message(Model):
    _from = ForeignKey(Users, on_delete='CASCADE')
    _to = ForeignKey(Users, on_delete='CASCADE')
    created_at = DateTimeField(auto_now=True)
    content = CharField(max_length=1000)


class Recipe(Model):
    name = CharField(max_length=50)
    description = CharField(max_length=1000)
    created_at = DateTimeField(auto_now=True)


class Ingredient(Model):
    name = CharField(max_length=20)
    amount = CharField(max_length=10)
    recipe = ForeignKey(Recipe, on_delete='CASCADE')
    _user = ForeignKey(Users, on_delete='CASCADE')
