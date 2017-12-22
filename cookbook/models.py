from collections import defaultdict
from .abstract import *
from hashlib import md5

from flask import url_for
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
        if isinstance(user, self.__class__):
            user = user.id

        user = int(user)
        if self.id == user:
            return

        relation = Relation.get(limit=1, _from=self, _to=user)

        if not relation:
            relation = Relation(_from=self, _to=user)
            relation.save()

            Notification(_from=self, _to=user,
                         link=url_for('cookbook.profile_page', username=self.username),
                         title='{} is following you!'.format(self.username),
                         content="click to see {}'s profile".format(self.username)).save()

    def unfollow(self, user):
        if isinstance(user, self.__class__):
            user = user.id

        user = int(user)
        if self.id == user:
            return

        relation = Relation.get(limit=1, _from=self, _to=user)

        if relation:
            relation[0].delete()

    def get_followers(self):
        followers = Relation.get(limit=None, _to=self, select_related=('_from', '_to'))
        return followers

    def get_followings(self):
        followings = Relation.get(limit=None, _from=self, select_related=('_from', '_to'))
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
    """
    Model representing the recipe table
    """

    name = CharField(max_length=50) #: Name of the recipe
    _user = ForeignKey(Users, on_delete='CASCADE') #: User which the recipe belongs to
    description = CharField(max_length=1000) #: description of the recipe
    created_at = DateTimeField(auto_now=True) #: recipe create date

    @classmethod
    def get_followings_posts(cls, _user):
        """
        Special SQL query for fetching the recipes of the user's followings to show on the home page

        :param Users _user: The user which the recipes will be fetched
        :return: A list of recipe objects with their ingredients and comments
        """
        recipe_fields = Recipe.get_fields(prefix=True)
        user_fields = Users.get_fields(prefix=True)
        ingredient_fields = Ingredient.get_fields(prefix=True)
        comment_fields = Comment.get_fields(prefix=True)

        s = """SELECT {} FROM recipe 
                INNER JOIN users ON (users.id = recipe._user)
                INNER JOIN ingredient ON (recipe.id = ingredient.recipe)
                LEFT OUTER JOIN comment ON (comment.recipe = recipe.id)
                WHERE users.id IN 
                    (SELECT (relation._to) FROM relation WHERE (relation._from = %s))
                ORDER BY recipe.created_at ASC, comment.created_at ASC"""

        s = s.format(','.join(recipe_fields + user_fields + ingredient_fields + comment_fields))

        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            cursor.execute(s, (_user.id,))

            rows = cursor.fetchall()

        output = []
        out_index = {}
        ingredient_set = defaultdict(set)
        comment_set = defaultdict(set)

        for row in rows:
            i = 0
            instance = cls()
            for field in recipe_fields:
                setattr(instance, field.split('.')[1], row[i])
                i += 1

            instance._user = Users()
            for field in user_fields:
                setattr(instance._user, field.split('.')[1], row[i])
                i += 1

            instance.ingredient_set = []
            instance.comments = []

            if instance.id not in out_index:
                out_index[instance.id] = len(output)
                output.append(instance)
            else:
                instance = output[out_index[instance.id]]

            ingredient = Ingredient()
            for field in ingredient_fields:
                setattr(ingredient, field.split('.')[1], row[i])
                i += 1

            if ingredient.id not in ingredient_set[instance.id]:
                ingredient_set[instance.id].add(ingredient.id)
                instance.ingredient_set.append(ingredient)

            comment = Comment()
            for field in comment_fields:
                setattr(comment, field.split('.')[1], row[i])
                i += 1

            if not comment.id:
                continue

            if comment.id not in comment_set[instance.id]:
                comment_set[instance.id].add(comment.id)
                instance.comments.append(comment)

        return output


class Ingredient(Model):
    """
    Represents an ingredient
    """
    name = CharField(max_length=50) #: name of the ingredient
    amount = CharField(max_length=50) #: amount of the ingredient
    recipe = ForeignKey(Recipe, on_delete='CASCADE') #: The recipe that the ingredient belongs to


class Relation(Model):
    _from = ForeignKey(Users, on_delete='CASCADE')
    _to = ForeignKey(Users, on_delete='CASCADE')


class Comment(Model):
    """
    Represents a comment
    """
    _user = ForeignKey(Users, on_delete='CASCADE') #: user that wrote the comment
    recipe = ForeignKey(Recipe, on_delete='CASCADE') #: recipe that the comment is written to
    text = CharField(max_length=140) #: Comment body
    created_at = DateTimeField(auto_now=True) #: Creation date


class Notification(Model):
    _from = ForeignKey(Users, on_delete='CASCADE')
    _to = ForeignKey(Users, on_delete='CASCADE')

    link = CharField(max_length=70)
    title = CharField(max_length=50)
    content = CharField(max_length=140)
    read = IntegerField(default=0)
    created_at = DateTimeField(auto_now=True)
