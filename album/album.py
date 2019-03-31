import sqlite3
import datetime
import uuid


from common.database_interface import Database
from common import name_util


class Album(object):

    def __init__(self):
        # Remove this later.
        self.db = Database('eigi-data.db')

    def count_photos_in_album(self, album_id):
        # Get count of photos in album.
        num_photos = self.db.make_query(
            '''
            SELECT COUNT(photo_id)
            FROM photo_album
            WHERE album_id = "{}"
            '''.format(album_id)
        )

        if len(num_photos) > 0:
            return num_photos[0][0]
        else:
            return 0

    def update_album_photo_count(self, album_id):
        new_count = self.count_photos_in_album(album_id)
        self.db.make_query(
            '''
            UPDATE album
            SET photos = {}
            WHERE album_id = "{}"
            '''.format(new_count, album_id)
        )

    def increment_views(self, album_id):
        self.db.make_query(
            '''
            UPDATE album
            SET views = views + 1
            WHERE album_id = "{}"
            '''.format(album_id)
        )

    def get_albums(self):
        """
        Returns all albums.
        """
        album_data = self.db.get_query_as_list(
            "select * from album order by date_created desc;"
        )

        rtn_dict = {

        }

        count = 0
        for album in album_data:
            album_cover_dict = self.get_album_cover(album['album_id'])
            # A new album may not have a preview image yet, this checks for it.
            if len(album_cover_dict) > 0:
                album['large_square'] = album_cover_dict[0]['large_square']

            album['human_readable_name'] = name_util.make_decoded(
                album['title'])

            album['human_readable_description'] = name_util.make_decoded(
                album['description'])

            rtn_dict[count] = album
            count += 1

        return rtn_dict

    def get_album(self, album_id):
        """
        Returns data about the album.
        """
        # Makes sure album photos count is correct.
        self.update_album_photo_count(album_id)

        # Update view count.
        self.increment_views(album_id)

        query = '''
                select * from album where album_id = {}
                '''.format(album_id)

        album_data = self.db.get_query_as_list(query)

        if len(album_data) > 0:
            album_data[0]['human_readable_title'] = name_util.make_decoded(
                album_data[0]['title'])

            album_data[0]['human_readable_description'] = name_util.make_decoded(
                album_data[0]['description'])

        if len(album_data) > 0 and album_data[0]['photos'] > 0:
            if self.get_album_cover(album_data[0]['album_id']):
                album_data[0]['large_square'] = self.get_album_cover(
                    album_data[0]['album_id'])[0]['large_square']
            return album_data[0]

        elif len(album_data) > 0:
            return album_data[0]
        else:
            return album_data

    def get_containing_album(self, photo_id):
        """
        Get the album that a photo belongs to.
        """
        query_string = '''
                SELECT album.album_id, album.title, album.views, album.description, album.photos, date_created
                FROM photo_album
                JOIN album ON(photo_album.album_id=album.album_id)
                WHERE photo_album.photo_id={}
        '''.format(photo_id)

        album_data = self.db.get_query_as_list(
            query_string
        )

        return album_data

    def get_album_cover(self, album_id):
        query_string = '''
                SELECT images.large_square FROM album
                JOIN photo_album on(album.album_id=photo_album.album_id)
                JOIN photo on(photo_album.photo_id=photo.photo_id)
                JOIN images on(images.photo_id=photo.photo_id)
                where album.album_id={}
                order by photo.date_uploaded asc limit 1

                        '''.format(album_id)

        album_cover = self.db.get_query_as_list(query_string)
        # print(album_cover)
        return album_cover

    def get_album_photos(self, album_id):
        # increment the view count
        self.increment_views(album_id)

        query_string = '''
                select album.title, album.album_id,
                album.description, album.views, album.photos,
                images.large_square,
                images.original,
                photo.photo_id, photo.date_taken,
                photo.photo_title, photo.date_uploaded,  photo.views
                from album
                JOIN photo_album on(album.album_id=photo_album.album_id)
                JOIN photo on(photo_album.photo_id=photo.photo_id)
                JOIN images on(images.photo_id=photo.photo_id)
                where album.album_id={}
                order by photo.date_taken asc
                '''.format(album_id)

        album_data = self.db.get_query_as_list(
            query_string
        )

        rtn_dict = {

        }

        count = 0
        for d in album_data:
            rtn_dict[count] = d
            count += 1

        print()
        print('here be dragons')
        print('\n', rtn_dict)

        if not rtn_dict:
            print(10 * '\nnope')
            album_data = self.get_album(album_id)
            print(album_data)
            rtn_dict = {
                0: album_data
            }
            return rtn_dict

        return rtn_dict

    def get_photo_album(self, album_id):
        """
        used to getting albums when deleting them
        """
        query = '''
        select * from photo_album where album_id = {}
        '''.format(album_id)

        photo_album_data = self.db.make_query(query)

        return photo_album_data

    def delete_album(self, album_id):
        # you have to delete from photo_album first
        # then from album, this is due to database constraints
        delete_from_photo_album = '''
        delete from photo_album where album_id = {}
        '''.format(album_id)

        resp = self.db.make_query(delete_from_photo_album)
        print(resp)

        delete_from_album = '''
        delete from album where album_id = {}
        '''.format(album_id)

        self.db.make_query(delete_from_album)

        # print()
        # print(self.get_album(album_id))
        # print(self.get_photo_album(album_id))
        # print()

        if not self.get_album(album_id) and not self.get_photo_album(album_id):
            return True

        return False

    def update_album(self, album_id, new_title, new_description):
        # you already know that it exists because otherwise the user wouldn't see it
        self.db.make_query('''
            update album
            set title = '{}', description = '{}'
            where album_id = '{}'
        '''.format(new_title, new_description, album_id)
        )

    def add_photos_to_album(self, album_id, photos):
        for photo in photos:
            """
            If the photo is already in the album it will cause an error.
            """
            try:
                self.db.make_query(
                    '''
                    INSERT INTO photo_album (photo_id, album_id)
                    VALUES ("{}", "{}")
                    '''.format(photo, album_id)
                )
            except Exception as err:
                print('add_photos_to_album, problem ', err)
            else:
                continue

        self.update_album_photo_count(album_id)

    def get_album_photos_in_range(self, album_id, limit=20, offset=0):
        """
        Returns the latest 20 photos.

        Offset is where results start from.
        """
        offset = int(offset)

        num_photos = self.count_photos_in_album(album_id)

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

        q_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (
                '''
                select photo.photo_title, photo.photo_id, album.album_id,
                album.title, photo.views, photo.date_uploaded, photo.date_taken,
                images.original, images.large_square
                from photo_album
                JOIN photo on(photo.photo_id=photo_album.photo_id)
                JOIN album on(photo_album.album_id=album.album_id)
                JOIN images on(photo.photo_id=images.photo_id)
                where album.album_id='{}'
                order by date_taken
                desc limit {} offset {}
                '''
            ).format(album_id, limit, offset)

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

        # print(data)

        a_dict = {}
        count = 0
        for d in data:
            a_dict[count] = d
            count += 1

        # Get data about the album itself
        album_data = self.get_album(album_id)
        rtn_dict = {'photos': a_dict}

        rtn_dict['album_data'] = album_data
        rtn_dict['limit'] = limit
        rtn_dict['offset'] = offset
        rtn_dict['page'] = page
        rtn_dict['pages'] = pages

        return rtn_dict

    def remove_photos_from_album(self, album_id, photos):
        for photo_id in photos:
            query_string = '''
                delete from photo_album
                where(photo_id='{}'
                and album_id='{}')
                '''.format(photo_id, album_id)

            self.db.make_query(query_string)

        # Make sure album photos count is correct.
        self.update_album_photo_count(album_id)

    def create_album(self, user_id, title, description):
        created = datetime.datetime.now()

        # identifier = str(int(uuid.uuid4()))[0:10]
        identifier = name_util.get_id()

        self.db.make_query(
            '''
            insert into album (album_id, user_id, views, title, description, photos, date_created, date_updated)
            values ("{}", "{}", {}, "{}", "{}", {}, "{}", "{}")
            '''.format(
                identifier,
                '28035310@N00',
                0,
                title,
                description,
                0,
                str(created),
                str(created)
            )
        )

        return identifier

    def get_albums_in_range(self, limit=20, offset=0):
        """
        Returns the latest 20 albums.

        Offset is where you want to start from, so 0 would be from the most recent.
        10 from the tenth most recent etc.
        """

        q_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (
                '''
                SELECT * FROM album
                ORDER BY date_created
                DESC LIMIT {} OFFSET {}
                '''
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

        for album in data:
            album_id = album['album_id']
            album_cover = self.get_album_cover(album_id)
            if len(album_cover) > 0:
                album['large_square'] = album_cover[0]['large_square']
            else:
                # Image preview for the album.
                album['large_square'] = '/static/images/logo.jpg'
            # Adding human readable title.
            album['human_readable_title'] = name_util.make_decoded(
                album['title'])

            album['human_readable_description'] = name_util.make_decoded(
                album['description'])

        a_dict = {}
        count = 0
        for d in data:
            a_dict[count] = d
            count += 1

        rtn_dict = {'albums': a_dict}

        rtn_dict['limit'] = limit
        rtn_dict['offset'] = offset

        return rtn_dict

    def get_album_by_name(self, album_name):
        data = self.db.make_query(
            '''
            select * from album where title = "{}"
            '''.format(album_name)
        )

        if len(data) > 0:
            return data


if __name__ == "__main__":
    a = Album()

    # print(a.get_containing_album(1968247294))

    print(a.get_albums_in_range(20, 0))

    # print(a.get_album(3149315074))

    # print(a.get_album_by_name("test 1"))

    # print(a.get_album_cover('72157650725849398'))
    # blah = a.get_albums()

    # print(a.create_album('28035310@N00', 'test', 'a test of creating an album'))

    # print(a.get_albums())

    # a.get_album('1847925474')

    # a.get_album_cover('1847925474')

    # print()
    # print(a.get_album_photos_in_range('72157701915517595'))
    # print()
    # print(a.get_album_photos('72157672063116008'))

    # print(a.remove_photos_from_album('72157678080171871', ['44692598005']))

    # print(a.update_album('72157678080171871',
    #                      'new album name', 'some album description'))

    # print(a.add_photos_to_album('72157677661532872',
    #                             [
    #                                 '31758038024', '45541535182', '31083915568'
    #                             ]))

    # print(blah.keys(), blah[0]['large_square'])

    # print(a.delete_album(72157671546432768))

    # print(a.get_album('72157664116903126'))

    # print(a.get_containing_album(16748114355))
