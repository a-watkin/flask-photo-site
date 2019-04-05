try:
    from common.photo_db_interface import Database
    from common.password_util import PasswordUtil
except ImportError as e:
    import os
    import sys
    sys.path.append(os.getcwd())
    from common.photo_db_interface import Database
    from common.password_util import PasswordUtil


class Admin(object):
    def __init__(self):
        self.db = Database()

    def make_account(self, username, password):
        self.db.make_query(
            '''
            INSERT INTO user (user_id, username, hash_value)
            VALUES ("{}", "{}", "{}")
            '''.format(
                username,
                username,
                PasswordUtil.hash_password(password))
        )


if __name__ == "__main__":
    a = Admin()
    a.make_account('', '')
