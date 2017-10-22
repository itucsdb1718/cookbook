from werkzeug.routing import Rule

from cookbook import app

url_map = [
    Rule('/initdb', endpoint='initdb'),
    Rule('/', endpoint='home_page'),
    Rule('/profile/', endpoint='profile_page'),
    Rule('/recipes/', endpoint='recipes_page'),
    Rule('/contact/', endpoint='contact_page'),
]

for rule in url_map:
    app.url_map.add(rule)
