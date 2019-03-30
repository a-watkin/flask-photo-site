import datetime
import os


PHOTOS_PATH = os.getcwd() + '/static/images'

# year/month
created = datetime.datetime.now()
print(created.year)
print(created.month)

files_in_file_path = os.listdir(PHOTOS_PATH)
print(files_in_file_path)

future_directory = PHOTOS_PATH + '/{}/{}'.format(created.year, created.month)
print(future_directory)

if not os.path.exists(future_directory):
    os.makedirs(future_directory)


print(created)
