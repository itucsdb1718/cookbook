from flask import Flask

app = Flask('cookbook')

from . import urls, views, models  # NOQA
