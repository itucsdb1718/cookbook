import os
from flask import Flask
from cookbook import cookbook


dsn = """user='{}' password='{}' host='{}' port={}
         dbname='{}'""".format('postgres', 'suheyl123', 'localhost', '5432', 'cookbook_db')

app = Flask(__name__, static_folder=None)
app.register_blueprint(cookbook)

app.config['dsn'] = dsn

if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True
    app.run(host='0.0.0.0', port=port, debug=debug)
