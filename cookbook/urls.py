from werkzeug.routing import Rule

from cookbook import cookbook
from . import views

url_map = [
    Rule('/initdb', endpoint='initdb'),
    Rule('/', endpoint='home_page'),
    Rule('/profile/', endpoint='profile_page'),
    Rule('/recipes/', endpoint='recipes_page'),
    Rule('/contact/', endpoint='contact_page'),
]

cookbook.add_url_rule('/', view_func=views.home_page)
cookbook.add_url_rule('/profile/', view_func=views.profile_page)
cookbook.add_url_rule('/recipes/', view_func=views.recipes_page)
cookbook.add_url_rule('/contact/', view_func=views.contact_page)
cookbook.add_url_rule('/initdb/', view_func=views.initdb)
