class KeywordHandler:
    def __init__(self, keywords):
        self.keywords = keywords

    def is_keyword(self, my_list, word):
        if word in my_list:
            return True
        else:
            return any(self.is_keyword(sublist, word) for sublist in my_list if isinstance(sublist, list))
