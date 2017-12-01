import datetime

from flask import render_template, redirect
from flask.helpers import url_for

from .models import Ingredient, Recipe, Users, CookBookPage, Messages


def initdb():
    Ingredient.create_table()
    Recipe.create_table()
    CookBookPage.create_table()
    return redirect(url_for('cookbook.home_page'))


def home_page():
    now = datetime.datetime.now()
    return render_template('home.html', current_time=now.ctime())


def profile_page():
    Users.drop()
    Messages.drop()

    Users.create()
    Messages.create()

    emre = Users(username='KEO', firstname='Kadir Emre', lastname='Oto',
                 email='otok@itu.edu.tr', password='1y2g434328grhwe')
    suheyl = Users(username='sühül', lastname='Karabela',
                   email='karabela@itu.edu.tr', password='1y47823h432434')

    emre.save()
    suheyl.save()

    message = Messages(_from=emre, _to=suheyl, content='Test Message 123')
    message.save()

    test = Users.get(limit=1, lastname='Karabela')[0]
    print(test.value('email'))

    mess = Messages.get(limit=1, _to=suheyl)[0]
    print(mess.value('content'))
    return render_template('profile.html')


def recipes_page():
    recipes = Recipe.get_all()
    return render_template('recipes.html', recipes=recipes)


def contact_page():
    return render_template('contact.html')
