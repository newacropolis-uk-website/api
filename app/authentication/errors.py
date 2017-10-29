class AuthenticationError(Exception):

    def __init__(self, username=None, password=None, message='Bad username or password'):
        self._username = username
        self._password = password
        self._message = message

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def error_message(self):
        return self._message
