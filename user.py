from common.database_interface import Database
from common.password_util import PasswordUtil


class User(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.user_id = None
        # init database
        self.db = Database('eigi-data.db')

    # check if username exists
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
        Returns the hasehd password from the database for the given username.
        """
        db_resp = self.db.get_row('user', 'username', self.username)
        return db_resp[2]

    def insert_hased_password(self, password):
        """
        Inserts hashed password into the database.

        Replaces password if already there.
        """
        # get hashed version
        hased_password = PasswordUtil.hash_password(password)
        self.db.make_query(
            '''
            update user 
            set hash_value = "{}"
            where username = "{}"
            '''.format(hased_password, self.username)
        )
        print(hased_password)

    def check_password(self):
        hashed_password = self.get_hashed_password(self.username)
        return PasswordUtil.check_hashed_password(self.password, hashed_password)


def main():
    pass


if __name__ == '__main__':
    main()
