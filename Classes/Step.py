import uuid


class Step(object):
    def __init__(self, dialogue_id=None, step_number=None):
        self.dialogue_id = dialogue_id
        self.step_id = uuid.uuid4()
        self.step_number = step_number
