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
            CREATE TABLE IF NOT EXISTS test_tag (
                tag_name TEXT NOT NULL UNIQUE,
                user_id TEXT NOT NULL,
                photos INT,
                PRIMARY KEY (tag_name, user_id)
                FOREIGN KEY(user_id) REFERENCES user(user_id) ON DELETE CASCADE
            );
            '''
        )
        print(resp)

    def copy_data(self):
        data = self.db.get_query_as_list(
            '''
            select * from tag
            '''
        )

        for tag in data:
            print()
            print(tag)

            count = self.db.get_query_as_list(
                '''
                select count(tag_name)
                from photo_tag
                where tag_name = '{}'
                '''.format(tag['tag_name'])
            )[0]['count(tag_name)']

            print(count)
            print()

            self.db.make_query(
                '''
                insert into test_tag (tag_name, user_id, photos)
                values('{}', '{}', {})
                '''.format(tag['tag_name'], '28035310@N00', count)
            )

    def make_upload_table(self):
        self.db.make_query(
            '''
            CREATE TABLE upload_photo(
                photo_id int 
                primary key unique not null, 
                user_id text not null, 
                foreign key(user_id) 
                references user(user_id) on delete cascade )
            '''
        )


def main():
    # make sure it's the right table...
    os.chdir(os.getcwd() + '/db-tag-count-column')
    print(os.getcwd())
    print(os.listdir())
    adb = AlterDB()
    # create temp table
    # adb.temp_tag_table()

    # copy everything from
    # adb.copy_data()

    # add the upload table to this db
    adb.make_upload_table()


if __name__ == "__main__":
    main()
