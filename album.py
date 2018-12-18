import sqlite3
import datetime
import uuid


from database_interface import Database
import name_util


class Album(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    def increment_views(self, album_id):
        self.db.make_query(
            '''
            update album
            set views = views + 1
            where album_id = "{}"
            '''.format(album_id)
        )

    def get_albums(self):
        """
        Returns all albums.
        """
        album_data = self.db.get_query_as_list(
            "select * from album order by date_created desc;"
        )

        # I also need an image to represent the album
        rtn_dict = {

        }

        count = 0
        for album in album_data:
            print('\n', 'album_id', album['album_id'])
            album_cover_dict = self.get_album_cover(album['album_id'])

            print(album_cover_dict)
            # a new album may not have this yet so check that there is a value first
            if len(album_cover_dict) > 0:
                album['large_square'] = album_cover_dict[0]['large_square']

            rtn_dict[count] = album
            count += 1

        return rtn_dict

    def get_album(self, album_id):

        # update view count
        self.increment_views(album_id)

        query = '''
        select * from album where album_id = {}
        '''.format(album_id)

        album_data = self.db.get_query_as_list(query)

        print(album_data)

        if len(album_data) > 0 and album_data[0]['photos'] > 0:
            # list index out of range
            # setting large square in the return data to the value returned by self.get_album_cover
            if self.get_album_cover(album_data[0]['album_id']):
                album_data[0]['large_square'] = self.get_album_cover(
                    album_data[0]['album_id'])[0]['large_square']

                album_data[0]['title'] = name_util.make_decoded(
                    album_data[0]['title'])

                album_data[0]['description'] = name_util.make_decoded(
                    album_data[0]['description'])

            print(album_data)
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

                select album.album_id, album.title, album.views, album.description, album.photos, date_created
                from photo_album
                join album on(photo_album.album_id=album.album_id)
                where photo_album.photo_id={}

        '''.format(photo_id)

        album_data = self.db.get_query_as_list(
            query_string
        )

        return album_data

    def get_album_cover(self, album_id):
        query_string = '''
                select images.large_square from album
                join photo_album on(album.album_id=photo_album.album_id)
                join photo on(photo_album.photo_id=photo.photo_id)
                join images on(images.photo_id=photo.photo_id)
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
                join photo_album on(album.album_id=photo_album.album_id)
                join photo on(photo_album.photo_id=photo.photo_id)
                join images on(images.photo_id=photo.photo_id)
                where album.album_id={}
                order by photo.date_uploaded asc
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
        # db.insert_data(
        #     table='tag',
        #     tag_name=new_tag,
        #     user_id='28035310@N00'
        # )
        for photo in photos:

            self.db.insert_data(
                table='photo_album',
                photo_id=photo,
                album_id=album_id
            )
            # i need to update the photo count in album

        # get the number of photos in the album after adding them
        query_string = '''
            SELECT COUNT(photo_id)
            FROM photo_album
            WHERE album_id='{}';
        '''.format(album_id)
        # update the count in album
        photo_count = self.db.make_query(query_string)[0][0]
        print(photo_count)

        # update the count in album
        query_string = '''
            UPDATE album
            SET photos = {}
            WHERE album_id='{}';
        '''.format(int(photo_count), album_id)
        self.db.make_query(query_string)

    def get_album_photos_in_range(self, album_id, limit=20, offset=0):
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
                '''
                select photo.photo_title, photo.photo_id, album.album_id,
                album.title, photo.views, photo.date_uploaded, photo.date_taken,
                images.original, images.large_square
                from photo_album
                join photo on(photo.photo_id=photo_album.photo_id)
                join album on(photo_album.album_id=album.album_id)
                join images on(photo.photo_id=images.photo_id)
                where album.album_id='{}'
                order by date_uploaded
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

        a_dict = {}
        count = 0
        for d in data:
            a_dict[count] = d
            count += 1

        rtn_dict = {'photos': a_dict}

        rtn_dict['limit'] = limit
        rtn_dict['offset'] = offset

        return rtn_dict

    def remove_photos_from_album(self, album_id, photos):
        for photo_id in photos:
            query_string = '''
                delete from photo_album
                where(photo_id='{}'
                and album_id='{}')
                '''.format(photo_id, album_id)

            self.db.make_query(query_string)

        # get the number of photos in the album after adding them
        query_string = '''
        SELECT COUNT(photo_id)
        FROM photo_album
        WHERE album_id='{}';
        '''.format(album_id)
        # update the count in album
        photo_count = self.db.make_query(query_string)[0][0]
        print(photo_count)

        # update the count in album
        query_string = '''
        UPDATE album
        SET photos = {}
        WHERE album_id='{}';

        '''.format(int(photo_count), album_id)
        self.db.make_query(query_string)

    def create_album(self, user_id, title, description):
        # one of the current ids, a ten digit number
        # 5053198694
        created = datetime.datetime.now()

        identifier = str(int(uuid.uuid4()))[0:10]

        self.db.insert_data(
            table='album',
            album_id=identifier,
            user_id='28035310@N00',
            views=0,
            title=title,
            description=description,
            photos=0,
            date_created=(str(created)),
            date_updated=(str(created))
        )

        print('album created with identifier ', identifier)

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
                select * from album
                order by date_created
                desc limit {} offset {}
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

        # print(data)

        for album in data:
            album_id = album['album_id']
            album_cover = self.get_album_cover(album_id)
            # print()
            if len(album_cover) > 0:
                # print(album_cover[0]['large_square'])
                album['large_square'] = album_cover[0]['large_square']
            else:
                # placeholder image
                album['large_square'] = '/static/images/logo.jpg'
            # print()
            # print(album)

            # album['large_square'] = self.get_album_cover(album['album_id'])[
            #     0]['large_square']
            # print()
            # print(album)

        a_dict = {}
        count = 0
        for d in data:
            a_dict[count] = d
            count += 1

        rtn_dict = {'albums': a_dict}

        rtn_dict['limit'] = limit
        rtn_dict['offset'] = offset

        return rtn_dict


if __name__ == "__main__":
    a = Album()
    # print(a.get_albums_in_range(20, 20))

    print(a.get_album(1621888039))

    # print(a.get_album_cover('72157650725849398'))
    # blah = a.get_albums()

    # print(a.create_album('28035310@N00', 'test', 'a test of creating an album'))

    # print(a.get_albums())

    # a.get_album('1847925474')

    # a.get_album_cover('1847925474')

    # print(a.get_album_photos_in_range('72157678080171871'))

    # print(a.remove_photos_from_album('72157678080171871', ['44692598005']))

    # print(a.update_album('72157678080171871',
    #                      'new album name', 'some album description'))

    # print(a.add_photos_to_album('72157677661532872',
    #                             [
    #                                 '31758038024', '45541535182', '31083915568'
    #                             ]))

    # print(blah.keys(), blah[0]['large_square'])

    # print(a.get_album_photos('72157650725849398'))

    # print(a.delete_album(72157671546432768))

    # print(a.get_album('72157664116903126'))

    # print(a.get_containing_album(16748114355))
