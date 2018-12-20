from passlib.hash import pbkdf2_sha512


class PasswordUtil(object):

    @staticmethod
    def hash_password(password):
        """
        Hashes a password using pbkdf2_sha512

        :param password: The sha512 passwrod from the login/register form
        :return: A sha512->pbkdf2_sha512 encrypted password
        """
        return pbkdf2_sha512.encrypt(password)

    @staticmethod
    def check_hashed_password(password, hashed_password):
        """
        Checks the password the user sent matches that of the database.
        The database password is encrypted more than the user's password at this stage.

        :param password: sha512-hashed password
        :param hashed_password: pbkdf2_sha512 encrypted password
        :return: True if the passwords match, false otherwise
        """
        try:
            return pbkdf2_sha512.verify(password, hashed_password)
        except Exception as e:
            print('check_hashed_password', e)
        else:
            return False


if __name__ == '__main__':
    # blah = PasswordUtil()
    # print(blah.hash_password("test"))

    print()
