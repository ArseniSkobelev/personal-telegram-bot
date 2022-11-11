import traceback
from pymongo import MongoClient
from Handlers.config import ConfigHandler
from Modules.log import Logger

_ch = ConfigHandler()


class Database(object):
    URI = _ch.get_key("DATABASE", "CONNECTION_URI")
    DATABASE = None

    @staticmethod
    def initialize():
        try:
            logger = Logger()
            client = MongoClient(Database.URI)
            Database.DATABASE = client[_ch.get_key("DATABASE", "NAME")]
            logger.log.info(_ch.get_key("LOG", "DB_CONNECTION_SUCCESS"))
        except Exception as error:
            logger.log.error(traceback.format_exc())

    @staticmethod
    def insert(collection, data):
        try:
            logger = Logger()
            Database.DATABASE[collection].insert_one(data)
            logger.log.info(_ch.get_key("LOG", "DB_INSERT_SUCCESS"))
        except Exception as error:
            logger.log.error(traceback.format_exc())

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)
