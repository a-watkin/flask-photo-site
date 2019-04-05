from common.photo_db_interface import Database
from common.password_util import PasswordUtil


class User(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.user_id = None
        # init database
        self.db = Database()

    def __str__(self):
        return """
        A user: \n
        username: {}\n
        user_id: {}\n
        password: {}\n
        using db: {}\n
        """.format(
            self.username,
            self.user_id,
            self.password,
            self.db.db_name
        )

    def check_for_username(self):
        """
        Checks if the username is in the database.
        """
        db_resp = self.db.get_row('user', 'username', self.username)
        if db_resp is None:
            return False
        return True

    def get_hashed_password(self, username):
        """
        Returns the hashed password from the database for the given username.
        """
        db_resp = self.db.get_row('user', 'username', self.username)
        return db_resp[2]

    def insert_hashed_password(self, password):
        """
        Inserts hashed password into the database.

        Replaces password if already there.
        """
        hashed_password = PasswordUtil.hash_password(password)
        self.db.make_query(
            '''
            update user 
            set hash_value = "{}"
            where username = "{}"
            '''.format(hashed_password, self.username)
        )

    def check_password(self):
        hashed_password = self.get_hashed_password(self.username)
        return PasswordUtil.check_hashed_password(self.password, hashed_password)


if __name__ == '__main__':
    pass
