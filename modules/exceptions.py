class NoDotEnvPathProvided(Exception):
    def __init__(self, value=None, *args, **kwargs):
        self.parameter = value
        for key, value in kwargs.items():
            setattr(self, key, value)

        for key, value in self.__dict__.items():
            print ("%s => %s" % ( key, value )) 

    def __str__(self):
        return repr(self.parameter)