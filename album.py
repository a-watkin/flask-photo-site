from database_interface import Database
import sqlite3


class Album(object):

    def __init__(self):
        self.db = Database('eigi-data.db')


if __name__ == "__main__":
    a = Album()
