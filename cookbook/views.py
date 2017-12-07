import datetime

from flask import render_template, redirect, flash
from flask.helpers import url_for
from flask import request
from flask_login.utils import login_required, login_user, current_user, logout_user

from .models import Ingredient, Recipe, Users, Message


def initdb():
    for model in [Users, Recipe, Ingredient, Message]:
        model.drop()

    for model in [Users, Recipe, Ingredient, Message]:
        model.create()

    emre = Users(username='KEO', firstname='Kadir Emre', lastname='Oto', email='otok@itu.edu.tr')
    suheyl = Users(username='sühül', lastname='Karabela', email='karabela@itu.edu.tr')

    emre.set_password("emre123")
    suheyl.set_password("suhul123")

    emre.save()
    suheyl.save()

    print(emre.check_password("keo123"))
    print(emre.check_password("emre123"))

    emre.username = '<KEO>'
    emre.save()

    message = Message(_from=emre, _to=suheyl, content='Test Message 123')
    message.save()
    return redirect(url_for('cookbook.home_page'))


def home_page():
    now = datetime.datetime.now()
    return render_template('layout.html', current_time=now.ctime())


@login_required
def profile_page():
    recipes = Recipe.get(limit=None, _user=current_user, prefetch=Ingredient.recipe)
    return render_template('profile.html', **locals())


def recipes_page():
    recipes = Recipe.get(limit=None, order_by='-description', prefetch=Ingredient.recipe)
    return render_template('recipes.html', recipes=recipes)


def contact_page():
    return render_template('old/contact.html')


def login():
    if request.method == 'POST':
        error = None

        username = request.form.get('username', 'x')
        password = request.form.get('password', 'x')

        users = Users.get(username=username, limit=1)

        if users and users[0].check_password(password):
            login_user(users[0])
            flash('You were successfully logged in')
            return redirect(request.referrer)

        else:
            error = 'Invalid credentials'

    return redirect(url_for('cookbook.profile_page'))


def logout():
    if current_user is not None:
        logout_user()

    return redirect(url_for('cookbook.home_page'))
