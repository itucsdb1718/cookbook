import psycopg2 as dbapi2

from .abstract import *
from hashlib import md5

from flask_login import UserMixin


class Users(UserMixin, Model):
    username = CharField(max_length=50, null=False)
    firstname = CharField(max_length=50, null=False, default='-')
    lastname = CharField(max_length=50, null=False)
    email = CharField(max_length=80, null=False)
    password = CharField(max_length=32, null=False)  # hash of password
    picture = CharField(max_length=100, default='default_profile.png')

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

    def follow(self, user):
        relation = Relation.get(limit=1, _from=self, _to=user)

        if not relation:
            relation = Relation(_from=self, _to=user)
            relation.save()

    def get_followers(self):
        followers = Relation.get(limit=None, _to=self)
        return followers

    def get_followings(self):
        followings = Relation.get(limit=None, _from=self)
        return followings


class Message(Model):
    _from = ForeignKey(Users, on_delete='CASCADE')
    _to = ForeignKey(Users, on_delete='CASCADE')
    created_at = DateTimeField(auto_now=True)
    content = CharField(max_length=1000)
    read = IntegerField(default=0)

    @staticmethod
    def get_messages(user1, user2, new=False):
        """
        Special query to fetch messages between users
        :param new: True if just new messages are needed; otherwise False
        :return: all messages between user1 and user2
        """

        statement = "SELECT DISTINCT _from, _to, created_at, content, read, message.id FROM message " \
                    "JOIN users ON (message._from = %s and message._to = %s) OR " \
                    "(message._from = %s and message._to = %s) {}ORDER BY created_at"

        statement = statement.format('WHERE message.read = 0' if new else '')

        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            cursor.execute(statement, (user1.id, user2.id, user2.id, user1.id))

            rows = cursor.fetchall()

        output = []

        for _from, _to, created_at, content, read, id in rows:
            if _from == user1.id:
                _from = user1
                _to = user2

            else:
                _from = user2
                _to = user1

            output.append(Message(_from=_from, _to=_to, created_at=created_at,
                                  content=content, read=read, id=id))

        return output


class Recipe(Model):
    name = CharField(max_length=50)
    _user = ForeignKey(Users, on_delete='CASCADE')
    description = CharField(max_length=1000)
    created_at = DateTimeField(auto_now=True)


class Ingredient(Model):
    name = CharField(max_length=20)
    amount = CharField(max_length=10)
    recipe = ForeignKey(Recipe, on_delete='CASCADE')


class Post(Model):
    _user = ForeignKey(Users, on_delete='CASCADE')
    recipe = ForeignKey(Recipe, on_delete='CASCADE')
    created_at = DateTimeField(auto_now=True)


class Relation(Model):
    _from = ForeignKey(Users, on_delete='CASCADE')
    _to = ForeignKey(Users, on_delete='CASCADE')
