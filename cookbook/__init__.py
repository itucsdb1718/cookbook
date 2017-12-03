from flask import Blueprint

cookbook = Blueprint('cookbook', __name__, template_folder='templates',
                     static_folder='static')

dsn = "user='{}' password='{}' host='{}' port={} dbname='{}'" \
    .format('postgres', 'suheyl123', 'localhost', '5432', 'cookbook_db')

from . import urls, views, models  # NOQA
