import uuid


class Dialogue(object):
    def __init__(self, title=None, current_step=1, userid=None, dialogue_type=None):
        self.dialogue_id = uuid.uuid4()
        self.title = title
        self.current_step = current_step
        self.userid = userid
        self.dialogue_type = dialogue_type
        self.status = "1"

    # Dialogue.status:
    # 0 - disabled
    # 1 - enabled

    def save(self):
        return vars(self)

    def next_step(self):
        self.current_step += 1
