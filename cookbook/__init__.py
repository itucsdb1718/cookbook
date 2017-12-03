from flask import Blueprint

cookbook = Blueprint('cookbook', __name__, template_folder='templates',
                     static_folder='static')


from . import urls, views, models  # NOQA
