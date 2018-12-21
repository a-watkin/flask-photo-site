from database_interface import Database

from password_util import PasswordUtil


class User(object):
    def __init__(self, username, password, _id=None):
        self.username = username
        self.password = password
        # the dot hex makes it a string
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
    # existing user
    u = User('eigi', 'test')
    print(u.check_for_username())

    # print('eigi' == u.check_for_username())
    # print(u.check_password())

    # non-existant user
    # u = User('adam', 'blah')
    # print(u.check_for_username())
    # print(u.check_password('test'))
    # print(u.get_hashed_password('eigi'))
    # print(u.insert_hased_password('test'))
    # print(u.check_password('test'))


if __name__ == '__main__':
    main()
