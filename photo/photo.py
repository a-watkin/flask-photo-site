import sqlite3
import urllib.parse


try:
    from common.database_interface import Database
    from common import utils
    from album.album import Album
    from photo_tag.photo_tag import PhotoTag
except Exception as e:
    import os
    import sys
    sys.path.append(os.getcwd())
    from common.database_interface import Database
    from common import utils
    from album.album import Album
    from photo_tag.photo_tag import PhotoTag


class Photo(object):

    def __init__(self):
        self.db = Database()
        self.tag = PhotoTag()
        self.album = Album()

    def count_photos(self):
        num_photos = self.db.make_query(
            '''
            SELECT COUNT(photo_id)
            FROM photo
            '''
        )

        if len(num_photos) > 0:
            return num_photos[0][0]
        else:
            return 0

    def get_photos_in_range(self, limit=20, offset=0):
        """
        Returns the latest 20 photos.

        Limit is the number of results returned.

        Offset is that start position of the returned results.
        """

        # There are two situation due to this number, even and odd
        num_photos = self.count_photos()

        if num_photos % 2 == 0:
            # Even number.
            if offset >= num_photos:
                offset = num_photos - (num_photos % 20) - limit

            page = offset // limit

            pages = num_photos // limit

            # Make the pages count start at 1.
            if num_photos == 20:
                page = 1
                pages = 1
            else:
                page += 1
                pages += 1

        else:
            # Odd number.
            if offset > num_photos:
                offset = num_photos - (num_photos % 20)

            page = offset // limit

            pages = num_photos // limit

            # Make the pages count start at 1.
            if num_photos == 20:
                page = 1
                pages = 1
            else:
                page += 1
                pages += 1

        query_string = (
            '''
            SELECT photo_id, views, photo_title, date_posted, date_taken, images.original, images.large_square FROM photo
            JOIN images USING(photo_id)
            ORDER BY date_posted
            DESC LIMIT ? OFFSET ?
            '''
        )

        values = (limit, offset)

        # Get photo data from the db.
        data = (self.db.get_s_query_as_list(query_string, values))

        rtn_dict = {
            'limit': limit,
            'offset': offset,
            'photos': []
        }

        for photo in data:
            photo['photo_title'] = utils.make_decoded(photo['photo_title'])

        a_dict = {}
        count = 0
        for d in data:
            a_dict[count] = d
            count += 1

        rtn_dict = {'photos': a_dict}

        rtn_dict['limit'] = limit
        rtn_dict['offset'] = offset
        rtn_dict['page'] = page
        rtn_dict['pages'] = pages

        return rtn_dict

    def get_date_posted(self, photo_id):
        photo_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            query_string = (
                '''
                SELECT date_posted FROM photo
                WHERE photo_id={}
                '''.format(photo_id)
            )

            photo_data = [x for x in c.execute(query_string)]

        if len(photo_data) < 1:
            return None
        else:
            return photo_data[0][0]

    def get_next_photo(self, photo_id):
        date_posted = self.get_date_posted(photo_id)

        photo_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            query_string = (
                '''
                SELECT * FROM photo JOIN images USING(photo_id)
                WHERE date_posted > '{}'
                ORDER BY date_posted ASC LIMIT 1
                '''.format(date_posted)
            )

            try:
                photo_data = [x for x in c.execute(query_string)]
            except Exception as e:
                print('Problem in getting next photo, ', e)

        if len(photo_data) < 1:
            return None
        else:
            return photo_data[0][0]

    def get_previous_photo(self, photo_id):
        date_posted = self.get_date_posted(photo_id)

        photo_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()
            next_string = (
                '''
                SELECT * FROM photo JOIN images USING(photo_id)
                WHERE date_posted < '{}'
                ORDER BY date_posted DESC LIMIT 1
                '''.format(date_posted)
            )

            photo_data = [x for x in c.execute(next_string)]

        if len(photo_data) < 1:
            return None
        else:
            return photo_data[0][0]

    def get_photo(self, photo_id):
        # Update view count.
        self.db.make_query(
            '''
            UPDATE photo
            SET views = views + 1
            WHERE photo_id = {}
            '''.format(photo_id)
        )

        rtn_data = {}
        photo_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()
            c.row_factory = sqlite3.Row

            query_string = (
                '''
                SELECT * FROM photo JOIN images USING(photo_id) WHERE photo_id={}
                '''.format(photo_id))

            photo_data = [dict(x) for x in c.execute(query_string)]

        next_photo = self.get_next_photo(photo_id)
        prev_photo = self.get_previous_photo(photo_id)

        # Prevent None being returned when the last pictures are reached.
        if next_photo is None:
            next_photo = photo_data[0]['photo_id']

        if prev_photo is None:
            prev_photo = photo_data[0]['photo_id']

        album_data = self.album.get_containing_album(photo_id)

        for album in album_data:
            album['human_readable_title'] = utils.make_decoded(
                album['title'])
            album['human_readable_description'] = utils.make_decoded(
                album['description']
            )
            album['large_square'] = self.album.get_album_cover(
                album['album_id'])[0]['large_square']

        if len(photo_data) > 0:
            # Because it is a list containing a dict.
            photo_data = photo_data[0]

            rtn_data = {
                'photo_id': photo_data['photo_id'],
                'title': utils.make_decoded(photo_data['photo_title']),
                'views': photo_data['views'],
                'tags': self.tag.get_photo_tags(photo_id),
                'album_data': album_data,
                'original': photo_data['original'],
                'next': next_photo,
                'previous': prev_photo,
                'albums': len(album_data)
            }

        return rtn_data

    def get_photos_range(self, table_name, start, stop):
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()
            return [x for x in c.execute("SELECT * FROM photos ".format(table_name))]

    def update_title(self, photo_id, new_title):
        resp = self.db.make_query('''
        UPDATE photo
        SET photo_title = '{}'
        WHERE photo_id = '{}'
        '''.format(new_title, photo_id)
        )

    def delete_photo(self, photo_id):
        # Update tag count, data for later update.
        tags = self.tag.get_photo_tags(photo_id)

        # Check if photo is in an album.
        album_check = self.db.make_query(
            '''
            SELECT * FROM photo_album WHERE photo_id = '{}'
            '''.format(photo_id)
        )

        # If the photo is in an album decrement the photos count.
        if len(album_check) > 0:
            for album in album_check:
                self.db.make_query(
                    '''
                    UPDATE album
                    SET photos = photos - 1
                    WHERE album_id = '{}'
                    '''.format(album[1])
                )

        # Delete photo from photo_album.
        self.db.make_query(
            '''
            DELETE FROM photo_album WHERE photo_id = '{}'
            '''.format(photo_id)
        )

        # Delete the photo itself.
        self.db.make_query(
            '''
            DELETE FROM photo WHERE photo_id = '{}'
            '''.format(photo_id)
        )

        # Remove EXIF data.
        self.db.make_query(
            '''
            DELETE FROM exif WHERE photo_id = '{}'
            '''.format(photo_id)
        )

        # remove photo from photo_tag
        self.db.make_query(
            '''
            DELETE FROM photo_tag WHERE photo_id = '{}'
            '''.format(photo_id)
        )

        # Update photo_tag count after deleting the photo.
        for tag in tags:
            if tag['tag_name']:
                print('tag name', tag['tag_name'])
                self.tag.update_photo_count(tag['tag_name'])


if __name__ == "__main__":
    p = Photo()
    print(p.get_photos_in_range(20, 0))
