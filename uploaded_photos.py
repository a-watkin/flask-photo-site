from database_interface import Database


class UploadedPhotos(object):
    """
    Handles a table of photos connected to a user.

    These represent recently uploaded files that have not had values set for things like title, tags etc.

    They will be stored in the table until they are saved.
    """

    def __init__(self):
        self.db = Database()


def main():
    up = UploadedPhotos()


if __name__ == "__main__":
    main()
