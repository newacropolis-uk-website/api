class AuthenticationError(Exception):

    def __init__(self, message='Bad username or password'):
        self.message = message

    @property
    def error_message(self):
        return self.message
