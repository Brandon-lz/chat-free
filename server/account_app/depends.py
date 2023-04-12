
from user_app.users import current_active_user
from user_app.db import User
from fastapi import Depends
from account_app.db import Account

async def get_account(user:User=Depends(current_active_user),):
    try:
        # account = (await Account.find(Account.user.id==user.id).to_list())[0]
        account = await Account.find_one(Account.user.id==user.id)
        return account
    except:
        raise Exception('未查询到用户账户')
