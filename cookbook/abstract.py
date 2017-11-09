

class Model(object):
    id = 0
    values = None

    def __init__(self, **kwargs):
        if self.values is None:
            self.values = {}

        for name in kwargs:
            self.__setattr__(name, kwargs[name])

    @classmethod
    def create(cls, connection):
        statement = "CREATE TABLE {} ({});"
        items = cls.__dict__

        columns = ['id SERIAL']

        for name in items:
            if name == 'id':
                raise Exception('"id" is default field!')

            if hasattr(items[name], '__sql__'):
                columns.append(name + ' ' + items[name].__sql__())

        columns.append('PRIMARY KEY (id)')
        statement = statement.format(cls.__name__, ', '.join(columns))

        cursor = connection.cursor()
        cursor.execute(statement)
        connection.commit()

    @classmethod
    def drop(cls, connection):
        statement = "DROP TABLE IF EXISTS " + cls.__name__ + " CASCADE"

        cursor = connection.cursor()
        cursor.execute(statement)
        connection.commit()

    def save(self, connection):
        fields = self.__class__.__dict__

        keys = []
        values = []

        for name in fields:
            if name != 'id' and hasattr(fields[name], '__sql__'):
                keys.append(name)
                values.append(self.values[name])

        if self.id:
            statement = "UPDATE {table} SET {keys} WHERE id={pk} RETURNING id"
            statement = statement.format(table=self.__class__.__name__,
                                         keys=', '.join(map(lambda x: x + "=%s", keys)),
                                         pk=self.id)

        else:
            statement = "INSERT INTO {table} ({keys}) VALUES ({values}) RETURNING id"
            statement = statement.format(table=self.__class__.__name__,
                                         keys=', '.join(keys),
                                         values=', '.join(["%s"]*len(values)))

        cursor = connection.cursor()
        cursor.execute(statement, values)
        connection.commit()

        self.id = self.id if self.id else cursor.fetchone()[0]

    def __setattr__(self, key, value):
        if hasattr(self.__class__.__dict__.get(key), '__sql__'):
            self.values[key] = value

            if isinstance(value, Model):  # if value is ForeignKey
                self.values[key] = value.id

        else:
            self.__dict__[key] = value

    def value(self, name):
        if name == 'id':
            return self.id

        return self.values[name]


class ForeignKey:
    def __init__(self, to, to_field=None, on_delete=None, on_update=None):
        self.to = to
        self.to_field = to_field
        self.on_delete = on_delete
        self.on_update = on_update

    def __sql__(self):
        statement = 'INTEGER REFERENCES {}'.format(self.to.__name__)

        if self.to_field is not None:
            statement += ' ({})'.format(self.to_field)

        if self.on_delete is not None:
            statement += ' ON DELETE {}'.format(self.on_delete)

        if self.on_update is not None:
            statement += ' ON UPDATE {}'.format(self.on_update)

        return statement

    def __setattr__(self, key, value):
        if key == 'value' and hasattr(value, 'id'):
            value = value.id

        self.__dict__[key] = value


class CharField(object):
    def __init__(self, max_length, null=True):
        self.max_length = max_length
        self.null = null

    def __sql__(self):
        statement = 'VARCHAR({})'.format(self.max_length)

        if not self.null:
            statement += ' NOT NULL'

        return statement


class IntegerField(object):
    pass


if __name__ == '__main__':
    import psycopg2 as dbapi2

    dsn = "user='{}' password='{}' host='{}' port={} dbname='{}'"\
        .format('keo', 'keo123', 'localhost', '5432', 'cookbook_db')


    class CookUser(Model):
        name = CharField(max_length=20)


    class CookTest(Model):
        a = CharField(30, null=False)
        b = ForeignKey(CookUser, on_delete='CASCADE')

        c = 10

        def asd(self, e):
            self.id = e


    with dbapi2.connect(dsn) as conn:
        CookTest.drop(conn)
        CookUser.drop(conn)

        CookUser.create(conn)
        CookTest.create(conn)

        emre = CookUser(name="Emre")
        user = CookUser(name="User")

        emre.save(conn)
        user.save(conn)

        print(emre.id)
        print(user.id)

        test1 = CookTest(a="This is char field", b=emre)
        test2 = CookTest(a="Hello world!", b=user)

        test1.save(conn)
        test2.save(conn)
