from Classes.Dialogue import Dialogue


class DialogueHandler:
    active_dialogues = None

    def __init__(self):
        self.active_dialogues = []

    def create_dialogue(self, title=None, userid=None):
        dialogue = Dialogue(title=title, userid=userid)
        self.active_dialogues.append(dialogue)

    def get_dialogues(self):
        return self.active_dialogues

    def get_dialogues_by_userid(self, userid):
        return_list = []

        for dialogue in self.active_dialogues:
            if dialogue.userid == userid:
                return_list.append(dialogue)
        return return_list

    def get_dialogue_by_title(self, title, userid):
        for dialogue in self.active_dialogues:
            if dialogue.title == title and dialogue.userid == userid:
                return dialogue

    def delete_dialogue(self, title):
        for index, dialogue in enumerate(self.active_dialogues):
            if dialogue.title == title:
                self.active_dialogues.pop(index)
            else:
                index = -1
