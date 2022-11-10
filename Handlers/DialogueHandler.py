from Classes.Dialogue import Dialogue


class DialogueHandler:
    active_dialogues = None

    def __init__(self):
        self.active_dialogues = []

    def create_dialogue(self, title=None, userid=None):
        dialogue = Dialogue(title)
        self.active_dialogues.append(dialogue)
        return dialogue

    def get_dialogues(self):
        return self.active_dialogues
