import datetime
from urls import app
from flask import render_template


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
