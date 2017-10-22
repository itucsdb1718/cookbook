import psycopg2 as dbapi2

from cookbook import app


dsn = """user='{}' password='{}' host='{}' port={}
         dbname='{}'""".format('postgres', 'suheyl123', 'localhost', '5432', 'cookbook_db')

app.config['dsn'] = dsn


def create_db():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS ingredient CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE ingredient (
                              id SERIAL,
                              name VARCHAR(50),
                              PRIMARY KEY (id)
                           );"""
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS recipe"""
        cursor.execute(query)

        query = """CREATE TABLE recipe (
                      id SERIAL,
                      name VARCHAR(100),
                      description VARCHAR(1000),
                      ingredient_id INTEGER REFERENCES ingredient,
                      PRIMARY KEY (id)
                   );"""
        cursor.execute(query)

        query = """INSERT INTO ingredient (name) VALUES ('domates')"""
        cursor.execute(query)

        connection.commit()
