from database_interface import Database
import sqlite3


class Album(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    def get_albums(self):
        """
        Returns all albums.
        """
        album_data = self.db.get_query_as_list(
            "select * from album;"
        )

        # I also need an image to represent the album

        rtn_dict = {

        }

        count = 0
        for album in album_data:
            rtn_dict[count] = album
            count += 1

        return rtn_dict


if __name__ == "__main__":
    a = Album()
    print(a.get_albums())
