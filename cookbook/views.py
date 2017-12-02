import datetime

from flask import render_template, redirect
from flask.helpers import url_for
from flask import request

from .models import Ingredient, Recipe, Users, Message


def initdb():
    Users.drop()
    Recipe.drop()
    Ingredient.drop()
    Message.drop()
    Users.create()
    Recipe.create()
    Ingredient.create()
    Message.create()

    emre = Users(username='KEO', firstname='Kadir Emre', lastname='Oto',
                 email='otok@itu.edu.tr', password='1y2g434328grhwe')
    suheyl = Users(username='sühül', lastname='Karabela',
                   email='karabela@itu.edu.tr', password='1y47823h432434')

    message = Message(_from=emre, _to=suheyl, content='Test Message 123')
    message.save()

    emre.save()
    suheyl.save()
    return redirect(url_for('cookbook.home_page'))


def home_page():
    now = datetime.datetime.now()
    return render_template('home.html', current_time=now.ctime())


def profile_page():
    suheyl = Users.get(limit=1, lastname='Karabela')[0]
    messages = Message.get(_to=suheyl, limit=None)
    return render_template('profile.html', **locals())


def recipes_page():
    recipes = Recipe.get(limit=None, order_by='-description')
    for recipe in recipes:
        recipe.ingredients = Ingredient.get(limit=None, recipe=recipe)
    return render_template('recipes.html', recipes=recipes)


def contact_page():
    return render_template('contact.html')
