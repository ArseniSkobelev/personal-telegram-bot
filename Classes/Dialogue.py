import uuid


class Dialogue(object):
    def __init__(self, title=None, current_step=None, userid=None):
        self.dialogue_id = uuid.uuid4()
        self.title = title
        self.steps = []
        self.current_step = current_step
        self.userid = userid

    def save(self):
        return vars(self)
