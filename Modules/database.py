import traceback
from pymongo import MongoClient
from Modules.env import EnvHandler
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
            logger.log.info("Database connection established successfully")
        except Exception as error:
            logger.log.error(traceback.format_exc())

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert_one(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    # def set_database(self, database_name):
    #     self.database_name = database_name

    # def connect(self):

    # def close(self):
    #     self.connection.close()

# -------------------- USAGE EXAMPLE --------------------
# from modules.database import DatabaseHandler
#
# db = DatabaseHandler(DB_NAME)
#
# item_1 = {
#   "item_name" : "Blender",
#   "max_discount" : "10%",
#   "batch_number" : "RR450020FRG",
#   "price" : 340,
#   "category" : "kitchen appliance"
# }

# db.connect()[COLLECTION_NAME].insert_one(item_1)
# db.close()
# -------------------- USAGE EXAMPLE --------------------
