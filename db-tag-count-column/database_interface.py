import os
import json
import sqlite3
import subprocess


class Database(object):

    def __init__(self, db_name=None):
        self.db_name = db_name

    def make_db(cls, name):
        from db_schema import create_database
        create_database(name)
        cls.db_name = name
        if os.path.isfile(name):
            return True
        else:
            print('Databse not created.')
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

    @classmethod
    def get_placeholders(cls, num):
        return ','.join(['?' for x in list(range(num))])

    def insert_data(self, **kwargs):
        """
        Expects any number of named arguments but must include a table name.

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

        # print(data, placeholders, table_name)

        # print('INSERT INTO {} VALUES({})'.format(
        #     table_name, placeholders))

        try:
            with sqlite3.connect(self.db_name) as connection:
                c = connection.cursor()
                c.executemany('INSERT INTO {} VALUES({})'.format(
                    table_name, placeholders), data)
        except Exception as e:
            print('Problem ', e)

    # def execute_query(self, query):
    #     with sqlite3.connect(self.db_name) as connection:
    #         c = connection.cursor()
    #         return [x for x in c.execute(query)]
    #         # print(row)

    def select_from_column(self, table_name, table_column):
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            # Like this because it was returning a list of tuples with trailing commas
            return [list(x)[0] for x in c.execute(
                "SELECT {} FROM {}".format(table_column, table_name))]

            # print(row)

    def get_rows(self, table_name):
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            return [x for x in c.execute("SELECT * FROM {}".format(table_name))]

            # return [list(x)[0] for x in c.execute("SELECT * FROM {}".format(table_name))]

            # print(row)

    def get_row(self, table_name, id_name, id_value):
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            for row in c.execute("SELECT * FROM {} WHERE {}= '{}' ".format(
                    table_name, id_name, id_value)):
                return list(row)
            # print(row)

    def get_query_as_list(self, query_string):
        q_data = None
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (query_string)

            q_data = c.execute(query_string)

        return [dict(ix) for ix in q_data]

    def make_query(self, query_string):
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            # print(query_string)
            return [x for x in c.execute(query_string)]

    def delete_rows_where(self, table_name, name, where):
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            query_string = '''
            delete from {} where {} = '{}'
            '''.format(table_name, name, where)

            try:
                print(query_string)
                c.execute(query_string)
            except Exception as e:
                print('Problem removing row ', e, query_string)

    def insert_tag_data(self, table_name, *args):
        for x in args[0]:

            try:
                with sqlite3.connect(self.db_name) as connection:
                    c = connection.cursor()
                    # INSERT INTO photo_tag VALUES(5052580779, 'london')
                    insert_string = '''INSERT INTO photo_tag VALUES({}, '{}')'''.format(
                        int(x[0]), x[1])

                    c.execute(insert_string)

            except Exception as e:
                print('Problem ', e, x)


def main():

    db = Database()
    db.db_name = 'eigi-data.db'

    new_tag = 'test'

    db.insert_data(
        table='tag',
        tag_name=new_tag,
        user_id='28035310@N00'
    )

    # db.delete_database()
    # db.make_db('eigi-data.db')

    # print(db.db_name)

    # print(db.get_photos_in_range())

    # print(db.get_photo(30081941117))

    # print(db.get_previous_photo(30081941117))

    # photo_id: 31734290228
    # print('current ', 31734290228)
    # print('next ', db.get_next_photo(31734290228))
    # print('previous ', db.get_previous_photo(31734290228))

    # print(db.get_date_posted(31734290578))
    # print()
    # print(db.get_photo(db.get_next_photo(31734290228)))

    # print(db.get_date_posted(44692598005))

    # print(db.get_all_users())

    """
    Creating and deleteing the database.
    """
    # db.delete_database()
    # db.make_db('eigi-data.db')
    # print(db.db_name)

    """
    Querying the data.
    """

    # print(db.get_row('photo', 'photo_id', '30081941117'))

    # for x in db.get_rows('photo'):
    #     print(x)

    """
    Inserting user data.
    """

    # db.insert_data(
    #     user_id='28035310@N00',
    #     username='eigi',
    #     hash='test',
    #     table='user'
    # )

    """
    Photo data.
    """
    # photo_id, user_id, views, photo_title, date_uploaded, date_posted, date_taken, date_updated
    # db.insert_data(
    #     photo_id='30081941117',
    #     user_id='28035310@N00',
    #     views=25,
    #     photo_title='tiles',
    #     date_uploaded="2016-07-31 15:53:03",
    #     date_posted="2016-07-31 15:53:03",
    #     date_taken="2016-07-31 15:53:03",
    #     date_updated="2016-07-31 15:53:03",
    #     table='photo'
    # )

    """
    Images data

    These are essentially the links for download.
    They can then be uploaded as the links for source.
    When a different host is found.
    """
    # Images
    # so you have to wrap it in a string for some reason
    # db.insert_data(
    #     images_id=str(uuid.uuid1()),
    #     square='/original',
    #     large_square='/original',
    #     thumbnail='/original',
    #     small='/original',
    #     small_320='/original',
    #     medium='/original',
    #     medium_640='/original',
    #     large='/original',
    #     original='/original',
    #     photo_id='30081941117',
    #     table='images'
    # )

    """
    Tag data.
    """
    # so for tags i need to make an api call for the photo data, inset the photo data
    # the tag data, update the linking table
    # i also need to do the same for the album and its linking table

    # Tag
    # db.insert_data(
    #     tag_id="6885045-4955715289-140955",
    #     tag_name='wigan',
    #     user_id='28035310@N00',
    #     table='tag'
    # )

    """
    Photo tag.

    Linking table.
    """
    # Photo tag
    # db.insert_data(
    #     photo_id="30081941117",
    #     tag_id="6885045-4955715289-140955",
    #     table='photo_tag'
    # )

    """
    Exif data.

    Exif id is not something in the data.
    It is not unique from photo_id
    """
    # db.insert_data(
    #     exif_id="6885045",
    #     exif_data=json.dumps({'key': 'value'}),
    #     photo_id="30081941117",
    #     table='exif'
    # )

    """
    Album data.

    Data about the album itself.
    """
    # db.insert_data(
    #     album_id="4955715289-140955",
    #     user_id='28035310@N00',
    #     title='vienna',
    #     views=20,
    #     table='album'
    # )

    """
    Photo album.

    Linking table, photos that are in an album.
    """
    # db.insert_data(
    #     album_id="4955715289-140955",
    #     photo_id='30081941117',
    #     table='photo_album'
    # )


if __name__ == "__main__":
    main()
