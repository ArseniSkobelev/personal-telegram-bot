from datetime import datetime


class Expense(object):
    now = datetime.now()

    def __init__(self, title="Dummy transaction", value=100, date=now, user_name="dummy_user"):
        self.title = title
        self.value = value
        self.user_name = user_name
        self.date = date

    def save(self):
        return vars(self)
