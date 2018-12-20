import os
import datetime


from database_interface import Database
from resize_photo import PhotoUtil

db = Database('eigi-data.db')

photo_ids = db.make_query(
    '''
    select photo_id from photo
    '''
)

# print(photo_ids)

for photo in photo_ids:
    print()
    photo_id = photo[0]

    # read date taken for the photo
    # 30081941117

    date_uploaded = db.make_query(
        '''
        select date_uploaded from photo where photo_id = "{}"
        '''.format(photo_id)
    )

    date_uploaded = date_uploaded[0][0]

    dt_obj = datetime.datetime.fromtimestamp(int(date_uploaded))

    filename = db.make_query(
        '''
        select original, large_square from images where photo_id = "{}"
        '''.format(photo_id)
    )
    split_filename = filename[0][0].split('/')
    filename_filename = split_filename[len(split_filename) - 1]

    split_filename = filename[0][1].split('/')
    large_square_filename = split_filename[len(split_filename) - 1]

    # print(filename)

    # # 2016-07-31 15:53:03
    # dt_obj = datetime.datetime.strptime("2016-07-31 15:53:03", "%Y-%m-%d %H:%M:%S")
    # print(dt_obj.hour)

    original_path = '/static/images/{}/{}/{}'.format(
        dt_obj.year, dt_obj.month, filename_filename)

    large_square_path = '/static/images/{}/{}/{}'.format(
        dt_obj.year, dt_obj.month, large_square_filename)

    print(original_path)
    print(os.getcwd() + original_path)
    print(os.getcwd() + large_square_path)

    large_square_dir = '/static/images/{}/{}/'.format(
        dt_obj.year, dt_obj.month)

    PhotoUtil.square_thumbnail(
        os.getcwd() + original_path, large_square_filename, os.getcwd() + large_square_dir, 300)

    db.make_query(
        '''
            update images
            set original = "{}", large_square = "{}"
            where photo_id = "{}"
            '''.format(original_path, large_square_path, photo_id)
    )

    # break
