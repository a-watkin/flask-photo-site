from database_interface import Database
import sqlite3
import urllib.parse


from tag import Tag
from album import Album
import name_util


class Photos(object):

    def __init__(self):
        self.db = Database('eigi-data.db')
        self.tag = Tag()
        self.album = Album()

    @classmethod
    def url_decode_tag(cls, tag_name):
        return urllib.parse.unquote(tag_name)

    @classmethod
    def needs_decode(cls, a_str):
        print(a_str)
        if a_str is None:
            return ""
        if '%' in a_str:
            return cls.url_decode_tag(a_str)
        else:
            return a_str

    def get_photos_in_range(self, limit=20, offset=0):
        """
        Returns the latest 20 photos.

        Offset is where you want to start from, so 0 would be from the most recent.
        10 from the tenth most recent etc.
        """
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

        """
        I think it may actually be better to layout what fields you want here.

        And maybe include all sizes.
        """

        data = [dict(ix) for ix in q_data]

        print()
        for photo in data:
            print('HERE', photo)
            photo['photo_title'] = self.needs_decode(photo['photo_title'])
            print(photo)
            print()

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
                where date_posted > '{}'
                order by date_posted asc limit 1
                '''.format(date_posted)
            )

            try:
                photo_data = [x for x in c.execute(query_string)]
            except Exception as e:
                print('Problem in getting next photo, ', e)

        # print(photo_data)

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

            # Problem here was that it was treating datetime as something other than a string
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

        print('PHOTO DATA\n', photo_data[0]['photo_id'])

        # prevent None being retunred when the last pictures are reached
        if next_photo is None:
            next_photo = photo_data[0]['photo_id']

        if prev_photo is None:
            prev_photo = photo_data[0]['photo_id']

        """
        Get the tags for the current photo.
        """
        tag_data = self.tag.get_photo_tags(photo_id)
        album_data = self.album.get_containing_album(photo_id)

        # print('tags ', tag_data)

        if len(album_data) > 0:
            # print('album_id', album_data[0]['album_id'])
            album_id = album_data[0]['album_id']
            album_cover = self.album.get_album_cover(album_id)
            # print(album_cover)
            album_data[0]['large_square'] = album_cover[0]['large_square']

        # print('album_data ', album_data)

        if len(photo_data) > 0:
            # becasuse it is a list containing a dict
            photo_data = photo_data[0]

            rtn_data = {
                'photo_id': photo_data['photo_id'],
                'title': self.needs_decode(photo_data['photo_title']),
                'views': photo_data['views'],
                'tags': tag_data,
                'containing_album': album_data,
                'original': photo_data['original'],
                'next': next_photo,
                'previous': prev_photo
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

        # print(resp)

    def delete_photo(self, photo_id):
        # Update tag count, data for later update
        tags = self.tag.get_photo_tags(photo_id)

        # check if photo is in an album
        album_check = self.db.make_query(
            '''
            select * from photo_album where photo_id = '{}'
            '''.format(photo_id)
        )

        print(album_check)

        # # if the photo is in an album decrement the value
        # # decrement the value of the album count
        if len(album_check) > 0:
            for album in album_check:
                print(album[1])

                self.db.make_query(
                    '''
                    update album
                    set photos = photos - 1
                    where album_id = '{}'
                    '''.format(album[1])
                )

        # delete photo from photo_album
        self.db.make_query(
            '''
            delete from photo_album where photo_id = '{}'
            '''.format(photo_id)
        )

        self.db.make_query(
            '''
            delete from photo where photo_id = '{}'
            '''.format(photo_id)
        )

        print(album_check)

        # update photo_tag count after deleting the photo
        for tag in tags:
            print('tag name', tag['tag_name'])
            self.tag.update_photo_count(tag['tag_name'])


if __name__ == "__main__":
    p = Photos()

    p.delete_photo(39974272161)
    # next photo is working
    # print(p.get_next_photo(44692597905))
    # it can't get that photo
    # print(p.get_photo(1823726615))

    # print(p.get_photos_in_range())
    # print(p.db.db_name)

    # p.update_title('30081941117', 'tenticles title')

    # p.delete_photo('5052578527')

    # not in an album
    # 43917844765
    # p.delete_photo('43917844765')

    # print(p.get_photo(1125251958))
