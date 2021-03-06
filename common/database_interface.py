import os
import json
import sqlite3
import subprocess


class Database(object):

    def __init__(self, db_name=None):
        self.db_name = db_name or 'eigi-data.db'

    def make_db(self):
        from photo_site_schema import create_database
        create_database(self.db_name)
        if os.path.isfile(self.db_name):
            return True
        else:
            print('Database not created.')
            return False

    @classmethod
    def delete_database(cls):
        if cls.db_name in os.listdir():
            try:
                os.remove(cls.db_name)
                cls.db_name = None
                return True
            except OSError as e:
                print('Problem: ', e)
        else:
            print('Database not found')
            return False

    @staticmethod
    def get_placeholders(num):
        return ','.join(['?' for x in list(range(num))])

    def insert_data(self, **kwargs):
        """
        Expects any number of named arguments but must include a table name.

        Expects data in this format:
        db.insert_data(
        table='tag',
        tag_name=new_tag,
        user_id='28035310@N00'
        )

        """

        table_name = kwargs['table']
        del kwargs['table']

        data = [tuple(kwargs.values())]

        placeholders = self.get_placeholders(len(kwargs))

        try:
            with sqlite3.connect(self.db_name) as connection:
                query_string = ('INSERT INTO {} VALUES({})'.format(
                    table_name, placeholders), data)

                c = connection.cursor()
                c.executemany('INSERT INTO {} VALUES({})'.format(
                    table_name, placeholders), data)
        except Exception as e:
            print('insert_data problem ', e)

    def select_from_column(self, table_name, table_column):
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            return [list(x)[0] for x in c.execute(
                "SELECT {} FROM {}".format(table_column, table_name))]

    def get_rows(self, table_name):
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            return [x for x in c.execute("SELECT * FROM {}".format(table_name))]

    def get_row(self, table_name, id_name, id_value):
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            for row in c.execute('''SELECT * FROM {} WHERE {} = "{}" '''.format(
                    table_name, id_name, id_value)):
                return list(row)

    def get_query_as_list(self, query_string):
        try:
            q_data = None
            with sqlite3.connect(self.db_name) as connection:
                c = connection.cursor()
                c.row_factory = sqlite3.Row
                q_data = c.execute(query_string)

            return [dict(ix) for ix in q_data]

        except Exception as e:
            print('Problem with query\n', query_string, e)

    def get_s_query_as_list(self, query_string, data):
        try:
            q_data = None
            with sqlite3.connect(self.db_name) as connection:
                c = connection.cursor()
                c.row_factory = sqlite3.Row
                q_data = c.execute(query_string, data)

            return [dict(ix) for ix in q_data]

        except Exception as e:
            print('Problem with query\n', query_string, e)

    def make_sanitized_query(self, query_string, data=None):
        print(query_string, data)
        try:
            with sqlite3.connect(os.path.join(self.db_name)) as connection:
                c = connection.cursor()
                return [x for x in c.execute(query_string, data)]
        except Exception as e:
            print('make_sanitized_query ', e)
            return []

    def make_query(self, query_string):
        print('passed query ', query_string)
        try:
            with sqlite3.connect(self.db_name) as connection:
                c = connection.cursor()
                return [x for x in c.execute(query_string)]
        except Exception as e:
            print('problem ', e)

    def delete_rows_where(self, table_name, name, where):
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            query_string = '''
            delete from {} where {} = "{}"
            '''.format(table_name, name, where)

            try:
                c.execute(query_string)
            except Exception as e:
                print('Problem removing row ', e, query_string)

    def insert_tag_data(self, table_name, *args):
        for x in args[0]:
            try:
                with sqlite3.connect(self.db_name) as connection:
                    c = connection.cursor()
                    insert_string = '''
                                    INSERT INTO photo_tag VALUES({}, "{}")
                                    '''.format(int(x[0]), x[1])
                    c.execute(insert_string)
            except Exception as e:
                print('Problem ', e, x)

    def get_column_names(self, table_name):
        """
        Get the column names for a table as a list.
        """
        columns = self.make_query(
            '''
            PRAGMA table_info( {} )
            '''.format(table_name)
        )

        column_names = []
        for x in columns:
            column_names.append(str(x[1]).strip().replace(' ', '_'))

        return column_names


if __name__ == "__main__":
    db = Database()
    db.make_db()
