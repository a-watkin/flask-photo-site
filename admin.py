from common.database_interface import Database
from password_util import PasswordUtil


class Admin(object):
    def __init__(self):
        self.db = Database('eigi-data.db')

    def make_account(self, username, password):
        self.db.make_query(
            '''
            insert into user (user_id, username, hash_value)
            values ("{}", "{}", "{}")
            '''.format(
                username,
                username,
                PasswordUtil.hash_password(password))
        )


def main():
    a = Admin()
    a.make_account('', '')


if __name__ == "__main__":
    main()
