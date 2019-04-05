import os
import uuid
import sqlite3
import json
import datetime

from common.database_interface import Database
from common import utils
from common.exif_util import ExifUtil
from photo_tag.photo_tag import PhotoTag


class UploadedPhotos(object):
    """
    Handles a table of photos connected to a user.

    These represent recently uploaded files that have not had values set for things like title, tags etc.

    Photos are stored in the table until they are saved.
    """

    def __init__(self):
        self.db = Database('eigi-data.db')
        self.user_id = '28035310@N00'

    def save_photo(self, photo_id, date_uploaded, original, large_square, exif_data, date_taken):
        exif_id = str(int(uuid.uuid4()))[0:10]

        # Write to EXIF table.
        self.db.make_sanitized_query(
            '''
            INSERT INTO exif(exif_id, exif_data, photo_id)
            VALUES (?,?,?)
            ''', (exif_id, exif_data, photo_id)
        )

        # Write to the uploaded_photo table.
        query_string = '''
            INSERT INTO upload_photo(photo_id, user_id)
            VALUES('{}', '{}')
            '''.format(photo_id, self.user_id)

        self.db.make_query(query_string)

        # Write to the photo table.
        self.db.make_query(
            '''
            INSERT INTO photo(photo_id, user_id, views, date_uploaded, date_taken)
            VALUES({},'{}', {}, '{}', '{}')
            '''.format(int(photo_id), self.user_id, 0, date_uploaded, str(date_taken))
        )

        # Write to images table.
        self.db.make_query(
            '''
            INSERT INTO images(photo_id, original, large_square)
            VALUES({},'{}','{}')
            '''.format(int(photo_id), original, large_square)
        )

    def get_uploaded_photos(self):
        q_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (
                '''
                SELECT * FROM upload_photo
                JOIN photo ON(photo.photo_id=upload_photo.photo_id)
                JOIN images ON(images.photo_id=upload_photo.photo_id)
                '''
            )

            q_data = c.execute(query_string)

        data = [dict(ix) for ix in q_data]

        t = PhotoTag()

        for photo in data:
            photo['tags'] = []
            # Get the title if it already has one.
            if photo['photo_title']:
                photo['photo_title'] = utils.make_decoded(
                    photo['photo_title'])
            # Get any tags the photo already has.
            for tag in t.get_photo_tags(photo['photo_id']):
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

    def discard_photo(self, photo_id):
        """
        Removes the specified photo from the photo and upload_photo tables.

        Also deletes the file from the disk.

        Returns True if the photo is not in the upload_photo table.
        """
        # Gets the relative path for the photo from the database.
        images_data = self.db.make_query(
            '''
            SELECT * FROM images WHERE photo_id = {}
            '''.format(photo_id)
        )

        # Uses the above relative path to get the path to the photo and remove it from the disk.
        if len(images_data) > 0:
            current_path = os.getcwd()
            photos_on_disk = []
            # The last returned element is the photo_id so to avoid that
            # I took the slice of everything up to that.
            for image in images_data[0][0:len(images_data[0]) - 1]:
                if image is not None:
                    photos_on_disk.append(os.path.join(current_path, image))

            for photo in photos_on_disk:
                try:
                    if os.path.isfile(photo):
                        os.remove(photo)
                except Exception as e:
                    print('Problem removing file ', e)

        # Remove photo from table photo.
        self.db.make_query(
            '''
            DELETE FROM photo WHERE photo_id = {}
            '''.format(photo_id)
        )

        # Remove photo from upload_photo table.
        self.db.make_query(
            '''
            DELETE FROM upload_photo WHERE photo_id = {}
            '''.format(photo_id)
        )

        upload_photos = self.get_uploaded_photos()

        for photo in upload_photos['photos']:
            if photo_id in upload_photos['photos'][photo]:
                return False

        return True

    def update_title(self, photo_id, new_title):
        self.db.make_query(
            '''
            UPDATE photo
            SET photo_title = '{}'
            WHERE photo_id = {}
            '''.format(new_title, photo_id)
        )

        # Check if title has been updated.
        data = self.db.make_query(
            '''
            SELECT * FROM photo WHERE photo_id = {}
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
                t = PhotoTag()
                tags = t.get_photo_tags(photo['photo_id'])
                for tag in tags:
                    if tag['tag_name']:
                        tag_name = utils.make_encoded(tag['tag_name'])
                        t.update_photo_count(tag_name)

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

            # Associate the photo with an album.
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
            DELETE FROM upload_photo
            '''
        )


if __name__ == "__main__":
    pass
