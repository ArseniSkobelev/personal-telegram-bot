from pathlib import Path
from dotenv import load_dotenv
import os
import modules.exceptions as Exceptions

class EnvHandler:
    def __init__(self, dotenv_path=None):
        if dotenv_path == None: raise Exceptions.NoDotEnvPathProvided()
        self.dotenv_path = Path(dotenv_path)
        load_dotenv(dotenv_path=self.dotenv_path)
    
    def get_env(self, env_header):
        return os.getenv(key=env_header, default=None)