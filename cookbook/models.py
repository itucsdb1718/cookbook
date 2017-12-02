import psycopg2 as dbapi2

from cookbook import cookbook
from .abstract import *


class Users(Model):
    username = CharField(max_length=50, null=False)
    firstname = CharField(max_length=50, null=False, default='-')
    lastname = CharField(max_length=50, null=False)
    email = CharField(max_length=80, null=False)
    password = CharField(max_length=32, null=False)  # hash of password


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
