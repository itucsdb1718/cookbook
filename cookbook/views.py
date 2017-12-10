import os
import json

from flask.helpers import url_for
from flask import render_template, redirect, flash, abort, Response
from flask import request, current_app, send_from_directory
from flask_login.utils import login_required, login_user, current_user, logout_user
from psycopg2 import IntegrityError

from .models import Ingredient, Recipe, Users, Message, Relation, Comment, Notification


def initdb():
    for model in [Users, Recipe, Ingredient, Message, Relation, Comment, Notification]:
        model.drop()

    for model in [Users, Recipe, Ingredient, Message, Relation, Comment, Notification]:
        model.create()

    emre = Users(username='KEO', firstname='Kadir Emre', lastname='Oto', email='otok@itu.edu.tr')
    suheyl = Users(username='sühül', firstname='Süheyl', lastname='Karabela', email='karabela@itu.edu.tr')

    emre.set_password("emre123")
    suheyl.set_password("suhul123")

    emre.save()
    suheyl.save()

    emre.follow(suheyl)

    print(emre.check_password("keo123"))
    print(emre.check_password("emre123"))

    emre.username = 'KadirEmreOto'
    emre.save()

    message = Message(_from=emre, _to=suheyl, content='Test Message 123')
    message.save()

    Message(_from=emre, _to=suheyl, content='Test Message2 123', read=1).save()
    Message(_from=suheyl, _to=emre, content='Test Message3 123', read=1).save()
    Message(_from=emre, _to=emre, content='Test Message4 123', read=1).save()

    recipe1 = Recipe(name='Kuru Fasülye', description='Mertcaaaaan', _user=emre)
    recipe2 = Recipe(name='Cacık', description='Short Description 3', _user=emre)
    recipe3 = Recipe(name='Pilav', description='Short Description 2', _user=suheyl)

    recipe1.save()
    recipe2.save()
    recipe3.save()

    fasulye = Ingredient(recipe=recipe1, amount='100 gr', name='Fasülye')
    domates = Ingredient(recipe=recipe1, amount='3 adet', name='Domates')
    biber = Ingredient(recipe=recipe1, amount='5 adet', name='Biber')

    salatalik = Ingredient(recipe=recipe2, amount='3 adet', name='Salatalık')
    yogurt = Ingredient(recipe=recipe2, amount='300 ml', name='Yoğurt')

    pirinc = Ingredient(recipe=recipe3, amount='1 kase', name='Pirinç')
    su = Ingredient(recipe=recipe3, amount='1L', name='Su')

    fasulye.save()
    domates.save()
    biber.save()
    salatalik.save()
    yogurt.save()
    pirinc.save()
    su.save()

    comments = [
        Comment(_user=suheyl, recipe=recipe1, text='such a great recipe!'),
        Comment(_user=emre, recipe=recipe1, text='this is bad'),
        Comment(_user=suheyl, recipe=recipe1, text='nononono'),
        Comment(_user=suheyl, recipe=recipe2, text='such a great recipe!'),
        Comment(_user=emre, recipe=recipe2, text='this is bad'),
        Comment(_user=suheyl, recipe=recipe3, text='nononono'),
    ]

    for c in comments:
        c.save()

    notifications = [
        Notification(_from=emre, _to=suheyl, title='You have a new message!',
                     content='Selam Süheyl :D', link=url_for('cookbook.message_page', username=suheyl.username)),

        Notification(_from=emre, _to=suheyl, title='You have a new message!',
                     content='Test message'*7, link=url_for('cookbook.message_page', username=suheyl.username)),

        Notification(_from=suheyl, _to=emre, title='Your recipe has new comment!',
                     content='Test message 1', link=url_for('cookbook.message_page', username=emre.username)),

        Notification(_from=suheyl, _to=emre, title='Your recipe has new comment!',
                     content='Test message 2', link=url_for('cookbook.message_page', username=emre.username))
    ]

    for n in notifications:
        n.save()

    return redirect(url_for('cookbook.home_page'))


@login_required
def home_page():
    recipes = Recipe.get_followings_posts(current_user)
    return render_template('home.html', recipes=recipes)


@login_required
def add_comment():
    if request.method == 'POST':

        if request.form.get('recipe', None) and request.form.get('text', None):
            recipe_id = int(request.form['recipe'].split('-')[1])
            comment = Comment(_user=current_user, recipe=recipe_id, text=request.form['text'])
            comment.save()
            return Response('success')
        return Response('failure')


def profile_page(username):
    user = Users.get(limit=1, username=username)
    if not user:
        abort(404)

    user = user[0]
    recipes = Recipe.get(limit=None, _user=user, prefetch=Ingredient.recipe)

    for recipe in recipes:
        recipe.comments = Comment.get(limit=None, order_by='created_at', recipe=recipe, select_related='_user')

    followers = user.get_followers()
    following = user.get_followings()

    followed = False

    if not current_user.is_anonymous:
        for u in followers:
            if u._from.id == current_user.id:
                followed = True
                break
    print(followed)
    return render_template('profile.html', **locals())


@login_required
def follow(user_id):
    print('FOLLOW:', user_id)
    current_user.follow(user_id)
    return redirect(request.referrer)


@login_required
def unfollow(user_id):
    print('UNFOLLOW:', user_id)
    current_user.unfollow(user_id)
    return redirect(request.referrer)


@login_required
def message_page(username):
    to = Users.get(limit=1, username=username)
    if not to:
        abort(404)

    to = to[0]
    messages = Message.get_messages(current_user, to)
    for message in messages:
        message.created_at = message.created_at.strftime("%m.%d.%Y %H:%M")

    return render_template('message.html', **locals())


@login_required
def new_messages(username):
    to = Users.get(limit=1, username=username)
    if not to:
        abort(404)

    output = []
    messages = Message.get_messages(current_user, to[0], new=True)

    for message in messages:
        m = {'from': 'me',
             'to': username,
             'time': message.created_at.strftime("%m.%d.%Y %H:%M"),
             'content': message.content,
             'id': message.id,
             'picture': url_for('cookbook.uploads', filename=current_user.picture)}

        if message._from.username == username:
            m['to'] = 'me'
            m['from'] = username
            m['picture'] = url_for('cookbook.uploads', filename=to[0].picture)

        print(m)

        output.append(m)
    return json.dumps(output)


@login_required
def view_message():
    if '_id' not in request.form:
        abort(404)

    message_id = request.form['_id']
    message = Message.get(limit=1, id=message_id, select_related='_to')

    if not message:
        abort(404)

    message = message[0]

    if message._to.username == current_user.username:
        message.read = 1
        message.save()
        return "true"

    return "false"


@login_required
def add_message():
    print(request.form, '*'*10)
    if 'id' not in request.form or 'content' not in request.form:
        abort(404)

    to = Users.get(limit=1, id=request.form['id'])

    if not to:
        abort(404)

    to = to[0]

    message = Message(_from=current_user, _to=to, content=request.form['content'])
    message.save()

    return 'true'


@login_required
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

        for name, amount in zip(names, amounts):
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


def recipe_page(recipe_id):
    recipe = Recipe.get(limit=None, id=recipe_id, select_related='_user', prefetch=Ingredient.recipe)[0]
    recipe.comments = Comment.get(limit=None, recipe=recipe, select_related='_user')
    if not recipe:
        return redirect(url_for('cookbook.recipes_page'))

    return render_template('recipe.html', recipe=recipe)


@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.get(limit=None, id=recipe_id, select_related='_user')[0]
    if recipe._user == current_user:
        # Delete model
        recipe.delete()
    return redirect(url_for('cookbook.recipes_page'))


def uploaded_file(filename):
    basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(basedir, filename)


@login_required
def upload_profile_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file.filename.split('.')[-1].lower() not in current_app.config['ALLOWED_EXTENSIONS']:
            flash('File dismissed (format error)!')
            return redirect(request.url)

        if file:
            basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   current_app.config['UPLOAD_FOLDER'])

            filename = 'profile-{}.{}'.format(current_user.id, file.filename.rsplit('.', 1)[-1])

            if not os.path.isdir(basedir):
                os.mkdir(basedir)

            file.save(os.path.join(basedir, filename))

            current_user.picture = filename
            current_user.save()

            return redirect(url_for('cookbook.profile_page', username=current_user.username))

    else:
        return '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <form method=post enctype=multipart/form-data>
              <p><input type=file name=file>
                 <input type=submit value=Upload>
            </form>
            '''


@login_required
def notification(id):
    item = Notification.get(limit=1, id=id, select_related='_to')
    if not item:
        abort(400)  # Bad Request

    item = item[0]
    if item._to.id != current_user.id:
        abort(400)  # Bad Request

    item.read = 1
    item.save()

    return redirect(item.link)


def login():
    if request.method == 'POST':
        if current_user.is_authenticated:
            flash('You are already logged in!')
            return redirect(url_for('cookbook.home_page'))

        username = request.form.get('username', 'x')
        password = request.form.get('password', 'x')

        users = Users.get(username=username, limit=1)

        if users and users[0].check_password(password):
            login_user(users[0])
            flash('You were successfully logged in')
            return redirect(url_for('cookbook.home_page'))

        else:
            flash('Username or password incorrect')
            return redirect(url_for('cookbook.login'))

    else:
        return render_template('login.html')


def logout():
    if current_user is not None:
        logout_user()

    return redirect(url_for('cookbook.login'))


def register():
    if request.method == 'POST' and current_user.is_anonymous:

        username = request.form.get('username', '')

        if len(username) < 3 or len(username) >= 50 \
                or request.form.get('password', '1') != request.form.get('password2', '2') \
                or 3 > len(request.form.get('password', '')):
            flash('Invalid form')
            return redirect(url_for('cookbook.login'))

        user = Users.get(limit=1, username=username)
        if user:
            flash('Username taken')
            return redirect(url_for('cookbook.login'))

        user = Users(username=username,
                     firstname=request.form.get('first-name', ''),
                     lastname=request.form.get('last-name', ''),
                     email=request.form.get('email'))
        user.set_password(request.form.get('password'))

        try:
            user.save()
        except IntegrityError as e:
            flash('Form invalid')
            print(e)
            return redirect(url_for('cookbook.login'))

        login_user(user)
        return redirect(url_for('cookbook.home_page'))

    return redirect(url_for('cookbook.login'))
