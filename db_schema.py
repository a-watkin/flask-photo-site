import sqlite3


def create_database(db_name):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS user( user_id TEXT PRIMARY KEY UNIQUE NOT NULL, username TEXT NOT NULL, hash_value TEXT NULL )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS album( album_id TEXT PRIMARY KEY UNIQUE NOT NULL, user_id TEXT, views INT, title TEXT UNIQUE NOT NULL, description TEXT, photos INT, date_created TEXT, date_updated TEXT, FOREIGN KEY(user_id) REFERENCES user(user_id) ON DELETE CASCADE )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS exif( exif_id TEXT PRIMARY KEY UNIQUE NOT NULL, exif_data BLOB, photo_id TEXT UNIQUE NOT NULL, FOREIGN KEY(photo_id) REFERENCES photo(photo_id) ON DELETE CASCADE )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS images( images_id TEXT, square TEXT, large_square TEXT, thumbnail TEXT, small TEXT, small_320 TEXT, medium TEXT, medium_640 TEXT, large TEXT, original TEXT, photo_id INT UNIQUE NOT NULL, FOREIGN KEY(photo_id) REFERENCES photo(photo_id) ON DELETE CASCADE )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS photo( photo_id INT PRIMARY KEY UNIQUE NOT NULL, user_id TEXT NOT NULL, views INT, photo_title TEXT, date_uploaded TEXT, date_posted TEXT, date_taken TEXT, date_updated TEXT, FOREIGN KEY(user_id) REFERENCES user(user_id) ON DELETE CASCADE )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS photo_album( photo_id TEXT REFERENCES photo(photo_id), album_id TEXT REFERENCES album(album_id), PRIMARY KEY (photo_id, album_id) )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS photo_album_dump( album_id TEXT PRIMARY KEY UNIQUE NOT NULL, photo_data BLOB )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS photo_dump( photo_id TEXT PRIMARY KEY UNIQUE NOT NULL, photo_data BLOB )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS photo_tag( photo_id INT REFERENCES photo(photo_id) on update cascade, tag_name TEXT REFERENCES tag(tag_name) on update cascade, PRIMARY KEY (photo_id, tag_name) )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS set_dump( set_id TEXT, set_data BLOB, PRIMARY KEY (set_id) )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS tag ( tag_name TEXT NOT NULL UNIQUE, user_id TEXT NOT NULL, photos INT, PRIMARY KEY (tag_name, user_id) FOREIGN KEY(user_id) REFERENCES user(user_id) ON DELETE CASCADE )
        '''
    )

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS upload_photo( photo_id int primary key unique not null, user_id text not null, foreign key(user_id) references user(user_id) on delete cascade )
        '''
    )


if __name__ == "__main__":
    create_database('eigi-data-2.db')
