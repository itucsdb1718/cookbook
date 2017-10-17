from flask import Flask
from werkzeug.routing import Map, Rule

app = Flask(__name__)

url_map = [
    Rule('/', endpoint='home_page'),
    Rule('/profile/', endpoint='profile_page'),
    Rule('/recipes/', endpoint='recipes_page'),
    Rule('/contact/', endpoint='contact_page'),
]

for rule in url_map:
    app.url_map.add(rule)
