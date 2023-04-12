from pydantic import BaseModel
from .db import Account
from pydantic import BaseModel, Field, SecretStr
import decimal
from beanie import  Link
from user_app.db import User
from typing import Optional


class AccountCreate(BaseModel):
    free:bool=False
    balance:decimal.Decimal 
    unit_cost:decimal.Decimal 


class AccountUpdate(BaseModel):
    free:Optional[bool] = None
    balance:decimal.Decimal 
    unit_cost:decimal.Decimal 