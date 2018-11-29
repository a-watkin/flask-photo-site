import sqlite3
import pickle
import os


def get_rows(table_name):
    with sqlite3.connect('eigi-data.db') as connection:
        c = connection.cursor()
        return [x for x in c.execute("SELECT * FROM {}".format(table_name))]


def pickle_obj(obj, filename):
    with open(filename, 'wb') as fh:
        # to pickle an item
        pickle.dump(obj, fh)


def unpickle_obj(filename):
    with open(filename, 'rb') as fh:
        # to unpickle an item
        return pickle.load(fh)


# get all rows for photo_tag
# save it as a dict?
files_in_dir = os.listdir(os.getcwd())

if 'pickled-photo-tag.pickle' not in files_in_dir:
    data = get_rows('photo_tag')
    print(data)
    pickle_obj(data, 'pickled-photo-tag.pickle')
else:
    # print('got it, loading data...')
    data = unpickle_obj('pickled-photo-tag.pickle')
    # print(data)
    # print('data laoded from pickle')


# drop photo_tag table from the database
def drop_table(table_name):
    with sqlite3.connect('eigi-data.db') as connection:
        c = connection.cursor()
        query_string = "DROP TABLE IF EXISTS {}".format(table_name)
        c.execute(query_string)


# drop_table('photo_tag')

# make a new photo tag table with cascade on the tag_name field

# photo_id is an int in photo
query_string = '''
CREATE TABLE IF NOT EXISTS photo_tag(
photo_id INT REFERENCES photo(photo_id) on update cascade,
tag_name TEXT REFERENCES tag(tag_name) on update cascade,
PRIMARY KEY (photo_id, tag_name)
);
                '''


def make_table(query_string):
    with sqlite3.connect('eigi-data.db') as connection:
        c = connection.cursor()
        c.execute(query_string)


print(make_table(query_string))
# print(data)
# make_table(query_string)


# add all the data back
def get_placeholders(num):
    return ','.join(['?' for x in list(range(num))])


def insert_data(table_name, *args):
    count = 0
    for x in args[0]:

        # print(x[0], x[1], '\n')

        placeholders = get_placeholders(len(x))
        # print(placeholders)

        try:
            with sqlite3.connect('eigi-data.db') as connection:
                c = connection.cursor()

                # INSERT INTO photo_tag VALUES(5052580779, 'london')
                insert_string = '''INSERT INTO photo_tag VALUES({}, '{}')'''.format(
                    int(x[0]), x[1])

                # print(insert_string, count)
                print(count)

                # c.executemany('INSERT INTO {} VALUES({})'.format(
                #     table_name, placeholders), (x[0], x[1]))

                c.execute(insert_string)
                count += 1

        except Exception as e:
            print('Problem ', e)


insert_data('photo_tag', data)


# test that it really does update
# seems to have updated
# what i need to check is that the cascade works
