import os
import datetime


from database_interface import Database

db = Database('eigi-data.db')
# read date taken for the photo
# 30081941117

date_taken = db.make_query(
    '''
    select date_taken from photo where photo_id = '30081941117'
    '''
)


filename = db.make_query(
    '''
    select original from images where photo_id = '30081941117'
    '''
)
split_filename = filename[0][0].split('/')
filename = split_filename[len(split_filename) - 1]

print(filename)

# 2016-07-31 15:53:03
dt_obj = datetime.datetime.strptime("2016-07-31 15:53:03", "%Y-%m-%d %H:%M:%S")
print(dt_obj.hour)


original_path = '/static/images/{}/{}/{}'.format(
    dt_obj.year, dt_obj.month, filename)

# large_square_path = '/static/images/{}/{}/{}'.format(
#     dt_obj.year, dt_obj.month, thumbnail_filename)

print(os.getcwd() + original_path)
