import os
import sqlite3
import datetime

from database_interface import Database
from tag import Tag
# from exif_util import ExifUtil


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

    def save_photo(self, photo_id, date_uploaded, original, large_square):
        # print(original)
        # get_datetime_taken(os.getcwd() + original)
        # print(photo_id, self.user_id)
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
            insert into images(photo_id, original, large_square)
            values({},'{}','{}')
            '''.format(int(photo_id), original, large_square)
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
                '''
                select * from upload_photo
                join photo on(photo.photo_id=upload_photo.photo_id)
                join images on(images.photo_id=upload_photo.photo_id)
                '''
            )

            q_data = c.execute(query_string)

        data = [dict(ix) for ix in q_data]

        # fix this later so that it doesn't suck
        for photo in data:
            photo['tags'] = []
            for tag in self.tag.get_photo_tags(photo['photo_id']):
                for t in tag.values():
                    photo['tags'].append(t)

        cur_dir = os.getcwd()

        a_dict = {}
        count = 0
        for d in data:
            a_dict[count] = d
            count += 1
            # d['original'] = cur_dir + d['original']
            # d['large_square'] = cur_dir + d['large_square']

        rtn_dict = {'photos': a_dict}

        return rtn_dict

    def get_uploaded_photos_test(self):
        # photo_id
        # from image the original size
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

        print(data)

        return {'photos': data}

        # cur_dir = os.getcwd()

        # a_dict = {}
        # count = 0
        # for d in data:
        #     a_dict[count] = d
        #     count += 1
        #     # d['original'] = cur_dir + d['original']
        #     # d['large_square'] = cur_dir + d['large_square']

        # rtn_dict = {'photos': a_dict}

        # return rtn_dict

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

        # remove photo from table photo
        self.db.make_query(
            '''
            delete from photo where photo_id = {}
            '''.format(photo_id)
        )

        # images should cascade delete, but check
        # Seems so

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
        # get the photo_id for eatch photo
        for photo in data.values():
            # set the date_posted to the current datetime
            date_posted = datetime.datetime.now()
            # get the photo_id
            print(photo['photo_id'], date_posted)
            # update the date_posted column in the table photo
            self.db.make_query(
                '''
                update photo
                set date_posted = '{}'
                where photo_id = {}
                '''.format(date_posted, photo['photo_id'])
            )

            test_data = self.db.make_query(
                '''
                select date_posted from photo
                where photo_id = {}
                '''.format(photo['photo_id'])
            )

            if test_data:
                # remove the photo from the table upload_photo
                self.db.make_query(
                    '''
                    delete from upload_photo
                    where photo_id = {}
                    '''.format(photo['photo_id'])
                )


def main():
    up = UploadedPhotos()

    up.add_to_photostream(
        {'0': {'date_posted': None, 'date_taken': None, 'date_updated': None, 'date_uploaded': '2018-12-11 08:21:10.870694', 'images_id': None, 'large': None, 'large_square': '/static/images/2018/12/test_landscape_1125251958_lg_sqaure.jpg', 'medium': None, 'medium_640': None,
               'original': '/static/images/2018/12/test_landscape_1125251958.jpg', 'photo_id': 1125251958, 'photo_title': None, 'small': None, 'small_320': None, 'square': None, 'tags': ['twat', 'slut'], 'thumbnail': None, 'user_id': '28035310@N00', 'views': 0}}
    )

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
