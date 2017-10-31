import psycopg2 as dbapi2

from cookbook import app


dsn = """user='{}' password='{}' host='{}' port={}
         dbname='{}'""".format('hasgul', 'hasgul', 'localhost', '5432', 'cookbook_db')

app.config['dsn'] = dsn

class Ingredient:
    @staticmethod
    def create_table():
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """DROP TABLE IF EXISTS ingredient_list CASCADE"""
            cursor.execute(query)

            query = """CREATE TABLE ingredient_list (
                                    id SERIAL PRIMARY KEY,
                                    name VARCHAR(50)
                                    );"""
            cursor.execute(query)

            query = """DROP TABLE IF EXISTS ingredient CASCADE"""
            cursor.execute(query)

            query = """CREATE TABLE ingredient (
                                  id SERIAL,
                                  name VARCHAR(50),
                                  amount VARCHAR(10),
                                  list_id INTEGER REFERENCES ingredient_list (id),
                                  PRIMARY KEY (id)
                               );"""
            cursor.execute(query)

            query = """INSERT INTO ingredient_list (name) VALUES ('domates')"""
            cursor.execute(query)
            query = """INSERT INTO ingredient (id, name, amount) VALUES (12, 'domates', '5kg')"""
            cursor.execute(query)
            query = """INSERT INTO ingredient (id, name, amount) VALUES (13, 'limon', '10kg')"""
            cursor.execute(query)
            query = """INSERT INTO ingredient (id, name, amount) VALUES (14, 'aasd', '2kg')"""
            cursor.execute(query)

            connection.commit()

    @staticmethod
    def get(name):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """SELECT * FROM ingredient WHERE (name = %s)"""
            cursor.execute(query, [name])
            return cursor.fetchall()


class Recipe:
    @staticmethod
    def create_table():
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

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
            connection.commit()

    @staticmethod
    def get(name):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """SELECT * FROM recipe WHERE (name = %s)"""
            cursor.execute(query, [name])
            return cursor.fetchall()


class CookBookUser():
    @staticmethod
    def create_table():
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """DROP TABLE IF EXISTS cookbook_user"""
            cursor.execute(query)

            query = """CREATE TABLE cookbook_user (
                          id SERIAL,
                          username VARCHAR(50) UNIQUE NOT NULL,
                          first_name VARCHAR(50) NOT NULL,
                          last_name VARCHAR(50) NOT NULL,
                          email VARCHAR(80) UNIQUE NOT NULL,
                          password CHAR(40) NOT NULL,
                          PRIMARY KEY (id)
                          );"""
            cursor.execute(query)
            connection.commit()
    @staticmethod
    def get(username):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """SELECT * FROM cookbook_user WHERE (username = %s)"""
            cursor.execute(query, [username])
            return cursor.fetchall()


class CookBookPage():
    @staticmethod
    def create_table():
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DROP TABLE IF EXISTS cookbook_page"""
            cursor.execute(query)

            query = """CREATE TABLE cookbook_page (
                          id SERIAL,
                          name VARCHAR(50) NOT NULL,
                          admin_user_id INTEGER REFERENCES cookbook_user,
                          password CHAR(40) NOT NULL,
                          PRIMARY KEY (id)
                          );"""
            cursor.execute(query)
            connection.commit()

    @staticmethod
    def get(name):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """SELECT * FROM cookbook_page WHERE (name = %s)"""
            cursor.execute(query, [name])
            return cursor.fetchall()
