import datetime

from flask import render_template, redirect
from flask.helpers import url_for

from cookbook import app
from .models import Ingredient, Recipe, CookBookUser, CookBookPage

@app.endpoint('initdb')
def initdb():
    Ingredient.create_table()
    Recipe.create_table()
    CookBookUser.create_table()
    CookBookPage.create_table()
    return redirect(url_for('home_page'))

@app.endpoint('home_page')
def home_page():
    now = datetime.datetime.now()
    return render_template('home.html', current_time=now.ctime())


@app.endpoint('profile_page')
def profile_page():
    return render_template('profile.html')


@app.endpoint('recipes_page')
def recipes_page():
    return render_template('recipes.html')


@app.endpoint('contact_page')
def contact_page():
    return render_template('contact.html')
