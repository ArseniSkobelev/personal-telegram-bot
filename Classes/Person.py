from Handlers.env import EnvHandler

env_handler = EnvHandler('./.env')


class Person():
    active_people = None

    def __init__(self, name=None, age=None, height=None, birthday=None, username=None, userid=None, weight=None):
        self.name = name
        self.age = age
        self.height = height
        self.weight = weight
        self.birthday = birthday
        self.username = username
        self.userid = userid
        self.active_people = self

    def set_name(self, name):
        self.name = name

    def set_age(self, age):
        self.age = age

    def set_height(self, height):
        self.height = height

    def set_birthday(self, birthday):
        self.birthday = birthday

    def set_username(self, username):
        self.username = username

    def set_userid(self, userid):
        self.userid = userid

    def save(self):
        return {
            "name": self.name,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "birthday": self.birthday,
            "username": self.username,
            "userid": self.userid
        }

    def create_person(self, userid=None):
        self.active_people = Person()

    def destroy_person(self):
        self.active_people = Person()


def authorize(userid):
    if str(userid) in env_handler.get_env("ALLOWED_USER_ID"):
        return True
    else:
        return False
