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


def main():
    up = UploadedPhotos()
    # up.save_photo('1234', '2018-12-09 03:52:57.905416')
    up.save_photo(
        '0001',
        '2018-12-09 03:52:57.905416',
        '/home/a/projects/flask-photo-site/static/images/2018/12/test_portrait_resized.jpg')


if __name__ == "__main__":
    main()
