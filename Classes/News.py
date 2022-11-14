from datetime import datetime


class Article(object):
    def __init__(self, title, url):
        self.title = title
        self.url = url
        self.date = datetime.now()

    def save(self):
        return {
            "title": self.title,
            "url": self.url,
            "date": self.date
        }
