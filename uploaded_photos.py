from database_interface import Database


class UploadedPhotos(object):
    """
    Handles a table of photos connected to a user.

    These represent recently uploaded files that have not had values set for things like title, tags etc.

    They will be stored in the table until they are saved.
    """

    def __init__(self):
        self.db = Database('eigi-data.db')
        self.user_id = '28035310@N00'

    def save_photo(self, photo_id, date_uploaded, original):
        print(photo_id, self.user_id)
        # write to the uploaded_photo table
        query_string = '''
        insert into upload_photo(photo_id, user_id)
        values('{}', '{}')
        '''.format(photo_id, self.user_id)

        print(query_string)

        self.db.make_query(query_string)

        # write to the photo table
        self.db.make_query(
            '''
            insert into photo(photo_id, user_id, views, date_uploaded)
            values({},'{}', {}, '{}')
            '''.format(int(photo_id), self.user_id, 0, date_uploaded)
        )

        # write to images
        self.db.make_query(
            '''
            insert into images(photo_id, original)
            values({},'{}')
            '''.format(int(photo_id), original)
        )

        # should probably get and store exif data

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

    def get_uploaded_photos(self):
        # photo_id
        # from image the original size
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


def main():
    up = UploadedPhotos()
    # up.save_photo('1234', '2018-12-09 03:52:57.905416')
    up.save_photo(
        '0001',
        '2018-12-09 03:52:57.905416',
        '/home/a/projects/flask-photo-site/static/images/2018/12/test_portrait_resized.jpg')


if __name__ == "__main__":
    main()
