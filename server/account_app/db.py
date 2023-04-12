import decimal
from beanie import Document, Link
from user_app.db import User
import uuid
from beanie import Indexed
import motor.motor_asyncio
import uuid

from pymongo import IndexModel
from pymongo.collation import Collation




DATABASE_URL = "mongodb://192.168.222.129:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client["chat-db4"]



decimal.getcontext().prec = 5


class Account(Document):
    user:Link[User]
    free:bool=False
    balance:decimal.Decimal = decimal.Decimal(0)      # 余额
    unit_cost:decimal.Decimal = decimal.Decimal('0')       # 每次花费
    
    class Settings:
        # email_collation = Collation("en", strength=2)
        indexes = [
            IndexModel("user", unique=True),
            # IndexModel(
            #     "email", name="case_insensitive_email_index", collation=email_collation
            # ),
        ]

