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

    recipe = Recipe(_user=suheyl, name='kuru fasulye', description='mertcan')
    recipe.save()

    Ingredient(recipe=recipe, name='fasulye', amount='1 kg').save()
    Ingredient(recipe=recipe, name='kuru', amount='sonsuz').save()

    recipe = Recipe(_user=suheyl, name='böfstrogonof', description='böf')
    recipe.save()

    Ingredient(recipe=recipe, name='böf', amount='1 kg').save()
    Ingredient(recipe=recipe, name='strogonof', amount='sonsuz').save()

    recipe = Recipe(_user=suheyl, name='su', description='iç')
    recipe.save()

    Ingredient(recipe=recipe, name='su', amount='1 Lt').save()

    return redirect(url_for('cookbook.home_page'))


def home_page():
    now = datetime.datetime.now()
    recipes = Recipe.get(limit=None, prefetch=Ingredient.recipe, select_related='_user')
    return render_template('home.html', current_time=now.ctime(), recipes=recipes)


@login_required
def profile_page():
    recipes = Recipe.get(limit=None, _user=current_user, prefetch=Ingredient.recipe)
    return render_template('profile.html', **locals())


def recipes_page():

    if request.method == 'POST':

        name = request.form.get('recipe-name', '')
        desc = request.form.get('desc', '')

        if len(name) < 2 or len(name) >= 50 or len(desc) >= 1000:
            return redirect('cookbook:recipes_page')

        recipe = Recipe(name=name, description=desc, _user=current_user)

        ingredients = []
        names = request.form.getlist('ing_name')
        amounts = request.form.getlist('ing_amount')

        if len(names) != len(amounts):
            return redirect('cookbook:recipes_page')

        for name, amount in zip(names,amounts):
            if len(name) < 2 or len(name) >= 20 \
                    or len(amount) < 1 or len(amount) >= 10:
                return redirect('cookbook:recipes_page')
            ingredients.append(Ingredient(name=name, amount=amount, recipe=recipe))

        if not ingredients:
            return redirect('cookbook:recipes_page')

        recipe.save()
        for i in ingredients:
            i.save()

    recipes = Recipe.get(limit=None, order_by='-created_at', _user=current_user, prefetch=Ingredient.recipe)
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
