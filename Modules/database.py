import traceback
from pymongo import MongoClient
from Handlers.env import EnvHandler
from Modules.log import Logger

env_handler = EnvHandler('./.env')


class Database(object):
    URI = env_handler.get_env("MONGODB_CONNECTION_URI")
    DATABASE = None

    @staticmethod
    def initialize():
        try:
            logger = Logger()
            client = MongoClient(Database.URI)
            Database.DATABASE = client[env_handler.get_env(
                "MONGODB_DB_NAME")]
            logger.log.info(env_handler.get_env(
                "DB_CONNECTION_SUCCESS"))
        except Exception as error:
            logger.log.error(traceback.format_exc())

    @staticmethod
    def insert(collection, data):
        try:
            logger = Logger()
            Database.DATABASE[collection].insert_one(data)
            logger.log.info(env_handler.get_env(
                "DB_INSERT_SUCCESS"))
        except Exception as error:
            logger.log.error(traceback.format_exc())

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)
