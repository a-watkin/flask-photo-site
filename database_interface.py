import os
import json
import sqlite3
import subprocess


class Database(object):

    def __init__(self, db_name=None):
        self.db_name = db_name

    def make_db(cls, name):
        from db_schema import create_database
        # db_schema.create_database(name)
        create_database(name)
        cls.db_name = name
        if os.path.isfile(name):
            return True
        else:
            print('Databse not created.')
            return False

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

    def get_placeholders(cls, num):
        return ','.join(['?' for x in list(range(num))])

    def insert_data(self, **kwargs):
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
            for row in c.execute("SELECT * FROM {} WHERE {}={}".format(
                table_name, id_name, id_value
            )):
                return list(row)
            # print(row)

    def get_photos_range(self, table_name, start, stop):
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            return [x for x in c.execute("SELECT * FROM photos ".format(table_name))]

    def get_all_tags(self):
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            return [x[0] for x in c.execute("SELECT tag_name FROM tag")]

    def get_photos_in_range(self, limit=20, offset=0):
        """
        Returns the latest 10 photos.

        Offset is where you want to start from, so 0 would be from the most recent.
        10 from the tenth most recent etc.
        """
        q_data = None
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (
                '''select photo_id, views, photo_title, date_uploaded, date_taken, images.original from photo
                join images using(photo_id)
                order by date_uploaded
                desc limit {} offset {}'''
            ).format(limit, offset)

            q_data = c.execute(query_string)

        rtn_dict = {
            'limit': limit,
            'offset': offset,
            'photos': []
        }

        """
        I think it may actually be better to layout what fields you want here.

        And maybe include all sizes.
        """

        data = [dict(ix) for ix in q_data]

        for d in data:
            rtn_dict['photos'].append(d)

        return rtn_dict

        # rtn_dict =
        # count = 0
        # for row in q_data:
        #     print(rtn_dict)
        #     rtn_dict[count] = [dict(ix) for ix in q_data]
        #     count += 1

        # rtn_dict['limit'] = limit
        # rtn_dict['offset'] = offset

        # return rtn_dict

    def get_date_posted(self, photo_id):
        photo_data = None
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()

            query_string = (
                '''
                select date_posted from photo
                where photo_id={}
                '''.format(photo_id)
            )

            photo_data = [x for x in c.execute(query_string)]

        if len(photo_data) < 1:
            return None
        else:
            return photo_data[0][0]

    def get_next_photo(self, photo_id):
        """
        you need the date that the current was uploaded
        """
        date_posted = self.get_date_posted(photo_id)

        photo_data = None
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()

            query_string = (
                '''
                select * from photo join images using(photo_id)
                where date_posted > {}
                order by date_posted asc limit 1
                '''.format(date_posted)
            )

            photo_data = [x for x in c.execute(query_string)]

        if len(photo_data) < 1:
            return None
        else:
            # print(photo_data)
            # the photo_id of the next photo
            return photo_data[0][0]

    def get_previous_photo(self, photo_id):

        date_posted = self.get_date_posted(photo_id)

        print(date_posted)

        photo_data = None
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()

            next_string = (
                '''
                select * from photo join images using(photo_id)
                where date_posted < {}
                order by date_posted desc limit 1
                '''.format(date_posted)
            )

            photo_data = [x for x in c.execute(next_string)]

        if len(photo_data) < 1:
            return None
        else:
            return photo_data[0][0]

    def get_photo(self, photo_id):
        rtn_data = {}
        photo_data = None
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            c.row_factory = sqlite3.Row

            query_string = (
                "select * from photo join images using(photo_id) where photo_id={}".format(photo_id))

            photo_data = [dict(x) for x in c.execute(query_string)]

        next_photo = self.get_next_photo(photo_id)
        prev_photo = self.get_previous_photo(photo_id)

        if len(photo_data) > 0:
            # becasuse it is a list containing a dict
            photo_data = photo_data[0]

            rtn_data = {
                'title': photo_data['photo_title'],
                'views': photo_data['views'],
                'original': photo_data['original'],
                'next': next_photo,
                'previous': prev_photo
            }

        return rtn_data


def main():

    db = Database()
    db.db_name = 'eigi-data.db'
    # db.delete_database()
    # db.make_db('eigi-data.db')

    # print(db.db_name)

    # print(db.get_photos_in_range())

    # print(db.get_photo(30081941117))

    # print(db.get_previous_photo(30081941117))

    # photo_id: 31734290228
    print('current ', 31734290228)
    print('next ', db.get_next_photo(31734290228))
    print('previous ', db.get_previous_photo(31734290228))

    print(db.get_date_posted(31734290578))
    print()
    print(db.get_photo(db.get_next_photo(31734290228)))

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