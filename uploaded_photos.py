import os
import uuid
import sqlite3
import json
import datetime

from common.database_interface import Database
from common import name_util
from exif_util import ExifUtil
from tag import Tag


class UploadedPhotos(object):
    """
    Handles a table of photos connected to a user.

    These represent recently uploaded files that have not had values set for things like title, tags etc.

    They will be stored in the table until they are saved.
    """

    def __init__(self):
        self.db = Database('eigi-data.db')
        self.user_id = '28035310@N00'
        self.tag = Tag()

    def save_photo(self, photo_id, date_uploaded, original, large_square, exif_data, date_taken):
        exif_id = str(int(uuid.uuid4()))[0:10]

        # Write to EXIF table.
        self.db.make_sanitized_query(
            '''
            insert into exif (exif_id, exif_data, photo_id)
            values (?,?,?)
            ''', (exif_id, exif_data, photo_id)
        )

        # Write to the uploaded_photo table.
        query_string = '''
        insert into upload_photo(photo_id, user_id)
        values('{}', '{}')
        '''.format(photo_id, self.user_id)

        self.db.make_query(query_string)

        # Write to the photo table.
        self.db.make_query(
            '''
            insert into photo(photo_id, user_id, views, date_uploaded, date_taken)
            values({},'{}', {}, '{}', '{}')
            '''.format(int(photo_id), self.user_id, 0, date_uploaded, str(date_taken))
        )

        # Write to images table.
        self.db.make_query(
            '''
            insert into images(photo_id, original, large_square)
            values({},'{}','{}')
            '''.format(int(photo_id), original, large_square)
        )

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
        q_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (
                '''
                select * from upload_photo
                join photo on(photo.photo_id=upload_photo.photo_id)
                join images on(images.photo_id=upload_photo.photo_id)
                '''
            )

            q_data = c.execute(query_string)

        data = [dict(ix) for ix in q_data]

        for photo in data:
            photo['tags'] = []
            if photo['photo_title']:
                photo['photo_title'] = name_util.make_decoded(
                    photo['photo_title'])
            for tag in self.tag.get_photo_tags(photo['photo_id']):
                for key, value in tag.items():
                    if key == 'human_readable_tag':
                        photo['tags'].append(value)

        a_dict = {}
        count = 0
        for d in data:
            a_dict[count] = d
            count += 1

        rtn_dict = {'photos': a_dict}

        return rtn_dict

    def get_uploaded_photos_test(self):
        q_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (
                '''
                select * from upload_photo
                join photo on(photo.photo_id=upload_photo.photo_id)
                join images on(images.photo_id=upload_photo.photo_id)
                '''
            )

            q_data = c.execute(query_string)

        data = [dict(ix) for ix in q_data]

        return {'photos': data}

    def discard_photo(self, photo_id):
        """
        Removes the specified photo from photo, upload_photo tables.
        Also deletes the files from the disk.

        Returns True if the photo is not in the upload_photo table.
        """
        # delete the files from the disk, you need to know the path to do this
        # which you should get from images
        images_data = self.db.make_query(
            '''
            select * from images where photo_id = {}
            '''.format(photo_id)
        )

        if len(images_data) > 0:
            print(images_data[0][0:len(images_data[0]) - 1])

            current_path = os.getcwd()
            photos_on_disk = []
            # the last returned element is the photo_id so to avoid that
            # I took the slice of everything up to that
            for image in images_data[0][0:len(images_data[0]) - 1]:
                if image is not None:
                    photos_on_disk.append(current_path + image)

            for photo in photos_on_disk:
                try:
                    os.remove(photo)
                except Exception as e:
                    print('Problem removing file ', e)
        else:
            print('no data')

        # Remove photo from table photo.
        self.db.make_query(
            '''
            delete from photo where photo_id = {}
            '''.format(photo_id)
        )

        # remove from upload_photo table
        self.db.make_query(
            '''
            delete from upload_photo where photo_id = {}
            '''.format(photo_id)
        )

        upload_photos = self.get_uploaded_photos()
        # print(upload_photos['photos'])

        for photo in upload_photos['photos']:
            # print()
            # print(upload_photos['photos'][photo])

            if photo_id in upload_photos['photos'][photo]:
                print('PROBLEM?')
                return False

        return True

        # IMPORTANT!
        # you should test this later after implementing adding tags to uploaded photos
        # remove from tags? i don't think you need to? you can have orphaned tags

    def update_title(self, photo_id, new_title):
        self.db.make_query(
            '''
            update photo
            set photo_title = '{}'
            where photo_id = {}
            '''.format(new_title, photo_id)
        )

        # check title has been updated
        data = self.db.make_query(
            '''
            select * from photo where photo_id = {}
            '''.format(photo_id)
        )

        if len(data) > 0:
            if data[0][3] == new_title:
                return True

        return False

    def add_to_photostream(self, data):
        for photo in data.values():
            date_posted = datetime.datetime.now()

            if photo['photo_title'] is None:
                check_title = self.db.make_query(
                    '''
                    SELECT photo_title FROM photo WHERE photo_id = {}
                    '''.format(photo['photo_id'])
                )

                if len(check_title) < 1:
                    self.db.make_query(
                        '''
                        UPDATE photo
                        SET photo_title = ''
                        WHERE photo_id = {}
                        '''.format(photo['photo_id'])
                    )

            # Update the date_posted column in the table photo.
            self.db.make_query(
                '''
                UPDATE photo
                SET date_posted = '{}'
                WHERE photo_id = {}
                '''.format(date_posted, photo['photo_id'])
            )

            test_data = self.db.make_query(
                '''
                SELECT date_posted from photo
                where photo_id = {}
                '''.format(photo['photo_id'])
            )

            if test_data:
                # Remove the photo from the table upload_photo/
                self.db.make_query(
                    '''
                    DELETE FROM upload_photo
                    WHERE photo_id = {}
                    '''.format(photo['photo_id'])
                )

                # Add the new tags.
                t = Tag()
                tags = t.get_photo_tags(photo['photo_id'])
                for tag in tags:
                    if tag['tag_name']:
                        Tag.update_photo_count(
                            name_util.make_encoded(tag['tag_name']))

    def add_all_to_album(self, album_id):
        uploaded_photos = self.db.make_query(
            '''
            SELECT * FROM upload_photo
            '''
        )

        for photo in uploaded_photos:
            photo_id = photo[0]

            date_posted = datetime.datetime.now()
            # Set published datetime.
            self.db.make_query(
                '''
                UPDATE photo
                SET date_posted = "{}"
                WHERE photo_id = {}
                '''.format(date_posted, photo_id)
            )

            self.db.make_query(
                '''
                INSERT INTO photo_album(photo_id, album_id)
                VALUES ('{}', '{}')
                '''.format(photo_id, album_id)
            )

            # Get photo count for album.
            photo_count = self.db.make_query(
                '''
                SELECT photos FROM album WHERE album_id = '{}'
                '''.format(album_id)
            )

            photo_count = int(photo_count[0][0]) + 1

            self.db.make_query(
                '''
                UPDATE album
                SET photos = {}
                WHERE album_id = '{}'
                '''.format(photo_count, album_id)
            )

        # Remove all rows from upload_photo table.
        self.db.make_query(
            '''
            delete from upload_photo
            '''
        )


def main():
    up = UploadedPhotos()

    # print(up.add_all_to_album('eh'))

    # up.add_to_photostream(
    #     {'0': {'date_posted': None, 'date_taken': None, 'date_updated': None, 'date_uploaded': '2018-12-11 08:21:10.870694', 'images_id': None, 'large': None, 'large_square': '/static/images/2018/12/test_landscape_1125251958_lg_sqaure.jpg', 'medium': None, 'medium_640': None,
    #            'original': '/static/images/2018/12/test_landscape_1125251958.jpg', 'photo_id': 1125251958, 'photo_title': None, 'small': None, 'small_320': None, 'square': None, 'tags': ['twat', 'slut'], 'thumbnail': None, 'user_id': '28035310@N00', 'views': 0}}
    # )

    # print(up.update_title(1269676143, 'test title'))

    # print(up.get_uploaded_photos())

    # 1326226897
    # print(up.discard_photo(1326226897))

    # up.save_photo('1234', '2018-12-09 03:52:57.905416')
    # up.save_photo(
    #     '0001',
    #     '2018-12-09 03:52:57.905416',
    #     '/home/a/projects/flask-photo-site/static/images/2018/12/test_portrait_resized.jpg')

    # up.save_photo(
    #     2429676854, '2018-12-09 21:16:43.708922', '/2018/12/test_landscape_3400128875_lg_sqaure.jpg', '/2018/12/test_landscape_3400128875_lg_sqaure.jpg'
    # )

    # print(up.get_uploaded_photos_test())


if __name__ == "__main__":
    main()
