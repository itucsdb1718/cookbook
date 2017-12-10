import json
import re
import os

from flask import Flask, redirect, url_for
from cookbook import cookbook, models
from flask_login import LoginManager


dsn = """user='{}' password='{}' host='{}' port={}
         dbname='{}'""".format('KEO', 'keo123', 'localhost', '5432', 'cookbook_db')

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__, static_folder=None)
app.register_blueprint(cookbook)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

app.secret_key = 'sdgfsdyfbhsdfysd'

login_manager = LoginManager()
login_manager.init_app(app)


def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn


@login_manager.user_loader
def user_loader(user_id):
    users = models.Users.get(id=user_id, limit=1)
    if users:
        return users[0]
    return None


@app.context_processor
def utility_processor():
    def notifications(user):
        n = models.Notification.get(limit=None, _to=user, read=0, select_related=('_from', '_to'))
        for i in n:
            i.created_at = i.created_at.strftime("%d.%m.%Y %H:%m")
        return n

    return dict(notifications=notifications)

  
@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('cookbook.login'))


if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True

    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = dsn

    app.run(host='0.0.0.0', port=port, debug=debug)
