from Modules.env import EnvHandler

env_handler = EnvHandler('./.env')


class Person:
    def __init__(self, name=None, age=None, height=None, birthday=None, username=None):
        self.name = name
        self.age = age
        self.height = height
        self.birthday = birthday
        self.username = username


def authorize(userid):
    if str(userid) in env_handler.get_env("ALLOWED_USER_ID"):
        return True
    else:
        return False
