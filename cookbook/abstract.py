import psycopg2 as dbapi2
from cookbook import dsn


class Model(object):
    id = 0
    values = None

    def __init__(self, **kwargs):
        if self.values is None:
            self.values = {}

        for name in kwargs:
            self.__setattr__(name, kwargs[name])

    @classmethod
    def create(cls):
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

        print(statement)
        with dbapi2.connect(dsn) as connection:
            cursor = connection.cursor()
            cursor.execute(statement)
            connection.commit()

    @classmethod
    def drop(cls):
        statement = "DROP TABLE IF EXISTS " + cls.__name__ + " CASCADE"

        with dbapi2.connect(dsn) as connection:
            cursor = connection.cursor()
            cursor.execute(statement)
            connection.commit()

    @classmethod
    def get(cls, limit=1, **kwargs):
        fields = [name for name in cls.__dict__ if hasattr(cls.__dict__[name], '__sql__')]
        fields.append('id')

        statement = "SELECT {keys} FROM {table} WHERE ({condition})"
        if limit:
            statement += " LIMIT {}".format(limit)

        keys = []
        values = []

        for key in kwargs:
            if key == 'id' or hasattr(cls, key):
                keys.append(key)

                if isinstance(kwargs[key], Model):  # if value is Foreign Key
                    values.append(kwargs[key].value('id'))

                else:
                    values.append(kwargs[key])
            else:
                raise NameError('{} is not a member of {}'.format(key, cls.__name__))

        statement = statement.format(keys=', '.join(fields),
                                     table=cls.__name__,
                                     condition=' AND '.join(map(lambda x: x + '=%s', keys)))

        with dbapi2.connect(dsn) as connection:
            cursor = connection.cursor()
            cursor.execute(statement, values)

            rows = cursor.fetchall()

        output = []

        for row in rows:
            instance = cls()
            for i, name in enumerate(fields):
                instance.__setattr__(name, row[i])

            output.append(instance)
        return output

    def save(self):
        fields = self.__class__.__dict__

        keys = []
        values = []

        for name in fields:
            if name != 'id' and hasattr(fields[name], '__sql__'):
                value = self.values.get(name, fields[name].default if hasattr(fields[name], 'default') else None)

                if value is not None:
                    keys.append(name)
                    values.append(value)

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

        print(statement, values)
        with dbapi2.connect(dsn) as connection:
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

        return self.values.get(name, None)


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
    def __init__(self, max_length, null=True, default=None):
        self.max_length = max_length
        self.null = null
        self.default = default

    def __sql__(self):
        statement = 'VARCHAR({})'.format(self.max_length)

        if not self.null:
            statement += ' NOT NULL'

        return statement


class IntegerField(object):
    def __init__(self, size=None, null=True, default=None):
        self.size = size
        self.null = null
        self.default = default

    def __sql__(self):
        statement = 'INTEGER' + ('({})'.format(self.size) if self.size is not None else '')

        if not self.null:
            statement += ' NOT NULL'

        return statement


class FloatField(object):
    def __init__(self, size=None, null=True, default=None):
        self.size = size
        self.null = null
        self.default = default

    def __sql__(self):
        statement = 'FLOAT' + ('({})'.format(self.size) if self.size is not None else '')

        if not self.null:
            statement += ' NOT NULL'

        return statement


class DateTimeField(object):
    def __init__(self, auto_now=False, null=True, default=None):
        self.auto_now = auto_now
        self.null = null

        self.default = default

    def __sql__(self):
        statement = 'TIMESTAMP' + (' DEFAULT NOW()' if self.auto_now else '')

        if not self.null:
            statement += ' NOT NULL'

        return statement

if __name__ == '__main__':
    class Users(Model):
        username = CharField(max_length=50, null=False)
        firstname = CharField(max_length=50, null=False, default='-')
        lastname = CharField(max_length=50, null=False)
        email = CharField(max_length=80, null=False)
        password = CharField(max_length=32, null=False)  # hash of password


    class Messages(Model):
        _from = ForeignKey(Users, on_delete='CASCADE')
        _to = ForeignKey(Users, on_delete='CASCADE')
        created_at = DateTimeField(auto_now=True)
        content = CharField(max_length=1000)
        

    Users.drop()
    Messages.drop()

    Users.create()
    Messages.create()

    emre = Users(username='KEO', firstname='Kadir Emre', lastname='Oto',
                 email='otok@itu.edu.tr', password='1y2g434328grhwe')
    suheyl = Users(username='sühül', lastname='Karabela',
                   email='karabela@itu.edu.tr', password='1y47823h432434')

    emre.save()
    suheyl.save()

    message = Messages(_from=emre, _to=suheyl, content='Test Message 123')
    message.save()

    test = Users.get(limit=1, lastname='Karabela')[0]
    print(test.value('email'))

    mess = Messages.get(limit=1, _to=suheyl)[0]
    print(mess.value('content'))
