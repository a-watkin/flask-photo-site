import sqlite3
import pickle
import os

from database_interface import Database


class AlterDB(object):
    def __init__(self):
        self.db = Database('eigi-data.db')

    def temp_tag_table(self):
        resp = self.db.make_query(
            '''
            CREATE TABLE IF NOT EXISTS test_photo_tag (
                photo_id  INT,
                tag_name  TEXT,
                photos INT,
                FOREIGN KEY(photo_id) REFERENCES photo(photo_id) on update cascade,
                PRIMARY KEY(photo_id,tag_name),
                FOREIGN KEY(tag_name) REFERENCES tag(tag_name) on update cascade
            );
            '''
        )
        print(resp)


def main():
    print(os.getcwd())

    adb = AlterDB()

    # adb.temp_tag_table()

    # get all rows for photo_tag
    # save it as a dict?

    # files_in_dir = os.listdir(os.getcwd())

    # insert_data('photo_tag', data)

    # test that it really does update
    # seems to have updated
    # what i need to check is that the cascade works


if __name__ == "__main__":
    main()
