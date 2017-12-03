import os
from flask import Flask
from cookbook import cookbook, models
from flask_login import LoginManager


dsn = """user='{}' password='{}' host='{}' port={}
         dbname='{}'""".format('postgres', 'suheyl123', 'localhost', '5432', 'cookbook_db')

app = Flask(__name__, static_folder=None)
app.register_blueprint(cookbook)

app.config['dsn'] = dsn
app.secret_key = 'sdgfsdyfbhsdfysd'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(user_id):
    users = models.Users.get(id=user_id, limit=1)
    if users:
        return users[0]
    return None


if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True
    app.run(host='0.0.0.0', port=port, debug=debug)
