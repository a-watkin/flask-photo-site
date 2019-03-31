import sqlite3
import urllib.parse


from common.database_interface import Database
from common import name_util
from tag import Tag
from album.album import Album


class Photos(object):

    def __init__(self):
        self.db = Database('eigi-data.db')
        self.tag = Tag()
        self.album = Album()

    def count_photos(self):
        num_photos = self.db.make_query(
            '''
            select count(photo_id)
            from photo
            '''
        )

        if len(num_photos) > 0:
            return num_photos[0][0]
        else:
            return 0

    def get_photos_in_range(self, limit=20, offset=0):
        """
        Returns the latest 20 photos.

        Offset is where you want to start from, so 0 would be from the most recent.
        10 from the tenth most recent etc.
        """

        num_photos = self.count_photos()

        if offset > num_photos:
            offset = num_photos - (num_photos % 20)

        page = offset // limit

        pages = num_photos // limit

        # Ensure pages start at 1 rather than 0.
        page += 1
        pages += 1

        # Get number of photos in database total.
        num_photos = self.db.make_query(
            '''
            select count(photo_id)
            from photo
            '''
        )[0][0]

        if offset > num_photos:
            offset = num_photos - (num_photos % 20)

        q_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (
                '''select photo_id, views, photo_title, date_posted, date_taken, images.original, images.large_square from photo
                join images using(photo_id)
                order by date_posted
                desc limit {} offset {}'''
            ).format(limit, offset)

            q_data = c.execute(query_string)

        rtn_dict = {
            'limit': limit,
            'offset': offset,
            'photos': []
        }

        # I think it may actually be better to layout what fields you want here.
        # And maybe include all sizes.
        data = [dict(ix) for ix in q_data]

        for photo in data:
            photo['photo_title'] = name_util.make_decoded(photo['photo_title'])

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
                where date_posted > '{}'
                order by date_posted asc limit 1
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

        print(date_posted)

        photo_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            # Problem here was that it was treating datetime as something other than a string.
            next_string = (
                '''
                select * from photo join images using(photo_id)
                where date_posted < '{}'
                order by date_posted desc limit 1
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
            update photo
            set views = views + 1
            where photo_id = {}
            '''.format(photo_id)
        )

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

        # Prevent None being returned when the last pictures are reached.
        if next_photo is None:
            next_photo = photo_data[0]['photo_id']

        if prev_photo is None:
            prev_photo = photo_data[0]['photo_id']

        album_data = self.album.get_containing_album(photo_id)

        for album in album_data:
            album['human_readable_title'] = name_util.make_decoded(
                album['title'])
            album['human_readable_description'] = name_util.make_decoded(
                album['description']
            )
            album['large_square'] = self.album.get_album_cover(
                album['album_id'])[0]['large_square']

        if len(photo_data) > 0:
            # Because it is a list containing a dict.
            photo_data = photo_data[0]

            rtn_data = {
                'photo_id': photo_data['photo_id'],
                'title': name_util.make_decoded(photo_data['photo_title']),
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
        update photo
        set photo_title = '{}'
        where photo_id = '{}'
        '''.format(new_title, photo_id)
        )

    def delete_photo(self, photo_id):
        # Update tag count, data for later update.
        tags = self.tag.get_photo_tags(photo_id)

        # Check if photo is in an album.
        album_check = self.db.make_query(
            '''
            select * from photo_album where photo_id = '{}'
            '''.format(photo_id)
        )

        print(album_check)

        # If the photo is in an album decrement the photos count.
        if len(album_check) > 0:
            for album in album_check:
                self.db.make_query(
                    '''
                    update album
                    set photos = photos - 1
                    where album_id = '{}'
                    '''.format(album[1])
                )

        # Delete photo from photo_album.
        self.db.make_query(
            '''
            delete from photo_album where photo_id = '{}'
            '''.format(photo_id)
        )

        # Delete the photo itself.
        self.db.make_query(
            '''
            delete from photo where photo_id = '{}'
            '''.format(photo_id)
        )

        # Remove EXIF data.
        self.db.make_query(
            '''
            delete from exif where photo_id = '{}'
            '''.format(photo_id)
        )

        # Update photo_tag count after deleting the photo.
        for tag in tags:
            if tag['tag_name']:
                print('tag name', tag['tag_name'])
                self.tag.update_photo_count(tag['tag_name'])


if __name__ == "__main__":
    p = Photos()

    # p.get_photos_in_range(20, 15280)

    # p.delete_photo(39974272161)
    # next photo is working
    # print(p.get_next_photo(44692597905))
    # it can't get that photo
    print(p.get_photo(1968247294))

    # print(p.get_photos_in_range())
    # print(p.db.db_name)

    # p.update_title('30081941117', 'tenticles title')

    # p.delete_photo('5052578527')

    # not in an album
    # 43917844765
    # p.delete_photo('43917844765')

    # print(p.get_photo(1125251958))
