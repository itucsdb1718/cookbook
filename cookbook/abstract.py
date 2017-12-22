import psycopg2 as dbapi2
from flask import current_app
from flask_login import current_user


class Model(object):
    """
    Base class for all models.
    """
    id = 0

    def __init__(self, **kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])

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
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            cursor.execute(statement)
            connection.commit()

    @classmethod
    def drop(cls):
        statement = "DROP TABLE IF EXISTS " + cls.__name__ + " CASCADE"

        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            cursor.execute(statement)
            connection.commit()

    @classmethod
    def get_fields(cls, prefix=None):
        return ['%s.id'%cls.__name__ if prefix else 'id'] + \
               ['%s.%s'%(cls.__name__, name) if prefix else name
                for name in cls.__dict__ if hasattr(cls.__dict__[name], '__sql__')]

    @classmethod
    def get(cls, limit=1, order_by=None, select_related=(), prefetch=None, **kwargs):
        """
        :param str order_by:
        :param int, None limit:
        :param select_related: for joining with another model based on field(s) of this model
        :type select_related: list, str
        :param prefetch: for joining with another model based on other's foreign key
        :type prefetch: ForeignKey
        """
        fields = cls.get_fields()

        related_fields = {}
        prefetch_fields = []

        statement = "SELECT *"
        table_statement = cls.__name__

        if select_related:
            if isinstance(select_related, str):
                select_related = [select_related]
            for field in select_related:
                st = ' INNER JOIN {name} as {field}{name} ON ({table}.{field} = {field}{name}.id)'\
                        .format(name=cls.__dict__[field].to.__name__,
                                table=cls.__name__,
                                field=field)

                related_fields[field] = cls.__dict__[field].to.get_fields()
                table_statement += st

        if prefetch:
            st = ' LEFT OUTER JOIN {name} as {field}{name} ON ({field}{name}.{field} = {table}.id)'\
                    .format(name=prefetch.owner.__name__,
                            field=prefetch._name,
                            table=cls.__name__)

            prefetch_fields.extend(prefetch.owner.get_fields())
            table_statement += st

        statement += ' FROM ' + table_statement

        if kwargs:
            statement += " WHERE ({condition})"

        if order_by:
            if order_by.startswith('-'):
                order_by = order_by[1:] + ' DESC'
            statement += ' ORDER BY ' + order_by

        if limit:
            statement += " LIMIT {}".format(limit)

        keys = []
        values = []

        for key in kwargs:
            if key == 'id' or hasattr(cls, key):
                keys.append(cls.__name__ + '.' + key)

                if isinstance(kwargs[key], Model) or isinstance(kwargs[key], current_user.__class__):  # if value is Foreign Key
                    values.append(kwargs[key].id)
                else:
                    values.append(kwargs[key])
            else:
                raise NameError('{} is not a member of {}'.format(key, cls.__name__))

        statement = statement.format(condition=' AND '.join(map(lambda x: x + '=%s', keys)))

        print(statement, values)
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            cursor.execute(statement, values)

            rows = cursor.fetchall()

        output = []
        out_index = {}

        for row in rows:
            instance = cls()
            i = 0
            for name in fields:
                setattr(instance, name, row[i])
                i += 1

            for field in select_related:
                f = cls.__dict__[field].to()
                for f_field in related_fields[field]:
                    setattr(f, f_field, row[i])
                    i += 1
                setattr(instance, field, f)

            if prefetch:
                related_instance = prefetch.owner()
                for name in prefetch_fields:
                    setattr(related_instance, name, row[i])
                    i += 1

                if instance.id not in out_index:
                    setattr(instance, prefetch.owner.__name__.lower() + '_set', [related_instance])
                else:
                    getattr(output[out_index[instance.id]], prefetch.owner.__name__.lower() + '_set')\
                        .append(related_instance)
                    continue

            out_index[instance.id] = len(output)
            output.append(instance)
        return output

    def save(self):
        fields = self.__class__.__dict__

        keys = []
        values = []

        for name in fields:
            if name != 'id' and hasattr(fields[name], '__sql__'):
                value = getattr(self, name)

                if isinstance(value, (Model, current_user.__class__)):
                    value = value.id

                if value is not None:
                    keys.append(name)
                    values.append(value)

        if self.id:
            statement = "UPDATE {table} SET {keys} WHERE id={pk} RETURNING id"
            statement = statement.format(table=self.__class__.__name__,
                                         keys=', '.join(map(lambda x: x + "=%s", keys)),
                                         pk=self.id)
        elif len(values) == 0:
            statement = "INSERT INTO {table} (id) VALUES (default) RETURNING id"
            statement = statement.format(table=self.__class__.__name__,
                                         keys=', '.join(keys))
        else:
            statement = "INSERT INTO {table} ({keys}) VALUES ({values}) RETURNING id"
            statement = statement.format(table=self.__class__.__name__,
                                         keys=', '.join(keys),
                                         values=', '.join(["%s"]*len(values)))

        print(statement, values)
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            cursor.execute(statement, values)
            connection.commit()

        self.id = self.id if self.id else cursor.fetchone()[0]

    def delete(self):

        if self.id == 0:
            return

        statement = 'DELETE FROM {} WHERE (id = %s)'.format(self.__class__.__name__)

        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            cursor.execute(statement, [self.id])
            connection.commit()


class BaseField:
    def __get__(self, instance, owner):
        if not instance:
            return self
        return instance.__dict__.get(self._name, getattr(self, 'default', None))

    def __set__(self, instance, value):
        instance.__dict__[self._name] = value

    def __set_name__(self, owner, name):
        self.owner = owner
        self._name = name


class ForeignKey(BaseField):
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


class CharField(BaseField):
    def __init__(self, max_length, null=True, default=None):
        self.max_length = max_length
        self.null = null
        self.default = default

    def __sql__(self):
        statement = 'VARCHAR({})'.format(self.max_length)

        if not self.null:
            statement += ' NOT NULL'

        return statement


class IntegerField(BaseField):
    def __init__(self, size=None, null=True, default=None):
        self.size = size
        self.null = null
        self.default = default

    def __sql__(self):
        statement = 'INTEGER' + ('({})'.format(self.size) if self.size is not None else '')

        if not self.null:
            statement += ' NOT NULL'

        return statement


class FloatField(BaseField):
    def __init__(self, size=None, null=True, default=None):
        self.size = size
        self.null = null
        self.default = default

    def __sql__(self):
        statement = 'FLOAT' + ('({})'.format(self.size) if self.size is not None else '')

        if not self.null:
            statement += ' NOT NULL'

        return statement


class DateTimeField(BaseField):
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
