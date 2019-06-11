from common.database_interface import Database
from common.password_util import PasswordUtil


class User(object):
    def __init__(self, username, password=None, user_id=None):
        self.username = username
        self.user_id = '28035310@N00'
        self.password = password
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

        if len(db_resp) == 3:
            return db_resp[2]
        else:
            return False

    def insert_hashed_password(self, password):
        """
        Inserts hashed password into the database.

        Replaces password if already there.
        """
        hashed_password = PasswordUtil.hash_password(password)
        self.db.make_query(
            '''
            UPDATE user 
            SET hash_value = "{}"
            WHERE username = "{}"
            '''.format(hashed_password, self.username)
        )

    def check_password(self):
        hashed_password = self.get_hashed_password(self.username)
        return PasswordUtil.check_hashed_password(self.password, hashed_password)

    def insert_user(self):
        """
        Can only run once per user as is.
        """
        self.db.make_query(
            '''
            INSERT INTO user (username, user_id)
            VALUES ("{}", "{}")
            '''.format(self.username, self.user_id)
        )

        self.insert_hashed_password(self.password)


if __name__ == '__main__':
    pass
