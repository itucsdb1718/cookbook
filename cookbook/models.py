import psycopg2 as dbapi2

from cookbook import app


dsn = """user='{}' password='{}' host='{}' port={}
         dbname='{}'""".format('postgres', 'suheyl123', 'localhost', '5432', 'cookbook_db')

app.config['dsn'] = dsn


class Ingredient:
    def __init__(self, id=None, name=None, amount=None):
        self.id = id
        self.name = name
        self.amount = amount

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
                                  list_id INTEGER REFERENCES ingredient_list (id) ON DELETE CASCADE,
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
    def __init__(self, id=None, name=None, desc=None, created_at=None, ingredients=None):
        self.id = id
        self.name = name
        self.description = desc
        self.created_at = created_at
        self.ingredients = ingredients

    def add_ingredient(self, name, amount, id=None):
        if not self.ingredients:
            self.ingredients = []
        self.ingredients.append(Ingredient(name=name, amount=amount, id=id))

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
                          created_at DATE,
                          ingredient_list_id INTEGER REFERENCES ingredient_list ON DELETE CASCADE,
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

            recipes = []
            for id, name, desc, _, created_at in cursor.fetchall():
                recipes.append([Recipe(id, name, desc, created_at)])

            return recipes


    @staticmethod
    def get_all():
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """SELECT recipe.id, recipe.name, recipe.description, recipe.created_at,
                              ingredient.id, ingredient.name, ingredient.amount
                        FROM recipe
                        JOIN ingredient_list ON recipe.ingredient_list_id = ingredient_list.id
                        JOIN ingredient ON ingredient_list.id = ingredient.list_id
                        ORDER BY recipe.name"""
            cursor.execute(query)

            row = cursor.fetchone()
            if not row:
                return []

            id, name, desc, created_at, ing_id, ing_name, ing_amount = row

            recipes = [Recipe(id, name, desc, created_at)]
            recipes[0].add_ingredient(ing_name, ing_amount, id)

            for row in cursor.fetchall():
                id, name, desc, created_at, ing_id, ing_name, ing_amount = row

                if name != recipes[-1].name:
                    recipes.append(Recipe(id, name, desc, created_at))

                recipes[-1].add_ingredient(ing_name, ing_amount, ing_id)

            return recipes


class CookBookUser:
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


class CookBookPage:
    @staticmethod
    def create_table():
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DROP TABLE IF EXISTS cookbook_page"""
            cursor.execute(query)

            query = """CREATE TABLE cookbook_page (
                          id SERIAL,
                          name VARCHAR(50) NOT NULL,
                          admin_user_id INTEGER REFERENCES cookbook_user ON DELETE CASCADE,
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
