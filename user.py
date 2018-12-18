from database_interface import Database

import password_util


class User(object):
    def __init__(self, username, password, _id=None):
        self.username = username
        self.password = password
        # the dot hex makes it a string
        self.user_id = None
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


def main():
    # existing user
    u = User('eigi', 'blah')
    # non-existant user
    # u = User('adam', 'blah')
    # print(u.check_for_username())
    # print(u.check_password('test'))
    print(u.get_hashed_password('eigi'))


if __name__ == '__main__':
    main()
