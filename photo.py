from database_interface import Database
import sqlite3


class Photos(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    def get_photos_in_range(self, limit=20, offset=0):
        """
        Returns the latest 10 photos.

        Offset is where you want to start from, so 0 would be from the most recent.
        10 from the tenth most recent etc.
        """
        q_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (
                '''select photo_id, views, photo_title, date_uploaded, date_taken, images.original, images.large_square from photo
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

        a_dict = {}
        count = 0
        for d in data:
            a_dict[count] = d
            count += 1

        rtn_dict = {'photos': a_dict}

        rtn_dict['limit'] = limit
        rtn_dict['offset'] = offset

        return rtn_dict

    def get_date_posted(self, photo_id):
        photo_data = None
        with sqlite3.connect(self.db.db_name) as connection:
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
        with sqlite3.connect(self.db.db_name) as connection:
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
        with sqlite3.connect(self.db.db_name) as connection:
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
        with sqlite3.connect(self.db.db_name) as connection:
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


if __name__ == "__main__":
    p = Photos()
    print(p.get_photos_in_range())
    # print(p.db.db_name)
