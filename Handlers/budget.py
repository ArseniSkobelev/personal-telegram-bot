from datetime import datetime
from Modules.database import Database
from Handlers.config import ConfigHandler


_ch = ConfigHandler()
_db = Database()


class Transaction(object):
    unit = None
    price = None
    date = datetime.now()
    product = None
    owner_id = None

    def __init__(self, owner_id):
        self.owner_id = owner_id

    def save(self):
        _db.initialize()
        _db.insert("transaction", self.db_ready())

    def __str__(self):
        return str({
            "unit": self.unit,
            "price": self.price,
            "date": self.date,
            "product": self.product,
            "owner_id": self.owner_id
        })

    def db_ready(self):
        return {
            "unit": self.unit,
            "price": self.price,
            "date": self.date,
            "product": self.product,
            "owner_id": self.owner_id
        }


class Budget(object):
    owner_id = None
    balance = 0
    is_updated = None
    last_update = None

    def __init__(self, owner_id):
        self.owner_id = owner_id
        self.is_updated = False

    def save(self):
        _db.initialize()
        _db.insert("budget", self.db_ready())

    def update(self, balance):
        self.balance = balance

    def __str__(self):
        return str({
            "owner_id": self.owner_id,
            "balance": self.balance,
            "is_updated": self.is_updated,
            "last_update": self.last_update
        })

    def db_ready(self):
        return {
            "owner_id": self.owner_id,
            "balance": self.balance,
            "is_updated": self.is_updated,
            "last_update": self.last_update
        }


class BudgetHandler():
    def __init__(self):
        pass

    @staticmethod
    def create_transaction(user_id):
        return Transaction(user_id)

    @staticmethod
    def create_budget(user_id):
        return Budget(user_id)
