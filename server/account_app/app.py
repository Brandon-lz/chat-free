
from beanie import init_beanie
from fastapi import Depends, FastAPI,APIRouter
from fastapi import Query,Body

from user_app.schemas import UserCreate, UserRead, UserUpdate
from user_app.users import auth_backend, current_active_user, fastapi_users
from .db import db,Account
from user_app.users import current_active_user,super_user
from user_app.db import User
from .schemas import AccountCreate,AccountUpdate
from account_app.depends import get_account
import decimal
from user_app.users import refresh_jwt
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException

from user_app.users import get_user_manager,UserManager
from fastapi_users.exceptions import UserNotExists


app = APIRouter(prefix='/account',tags=['account'])

@app.post('/create-account')
async def create_account(user:User=Depends(current_active_user),account_in:AccountCreate=None):
    try:
        account = await Account(user=user.id,**account_in.dict(exclude_unset=True)).create()
    except DuplicateKeyError:
        raise HTTPException(status_code=410,detail='用户账户已经创建，不能重复创建')
    return account.dict()


@app.get('/user-account')
async def user_account(
    account:Account=Depends(get_account),
    set_jwt = Depends(refresh_jwt)
):
    print(account)
    return account


@app.get('/manager-get-user-account')
async def manager_get_user_account(
    super_user:User=Depends(super_user),
    user_manager:UserManager=Depends(get_user_manager),
    target_email:str=Query(default=None,description='email'),
):
    try:
        target_user = await user_manager.get_by_email(target_email)
    except UserNotExists:
        raise HTTPException(status_code=400,detail='未找到目标账户')
    account = await Account.find_one(Account.user.id==target_user.id)
    return account


@app.patch('/user-account')
async def update_user_account(account:Account=Depends(get_account),new_account:AccountUpdate=None):
    data = new_account.dict(exclude_unset=True)      # 只会返回传了的数据
    # print(data)
    
    account.free = data.get('free') if data.get('free')!=None else account.free
    account.balance = data.get('balance') if data.get('balance')!=None else account.balance
    account.unit_cost = data.get('unit_cost') if data.get('unit_cost')!=None else account.unit_cost
    
    await account.save()
    return account


@app.patch('/account-deal')
async def account_deal(account:Account=Depends(get_account),cost:decimal.Decimal=0,
    set_jwt = Depends(refresh_jwt)
):
    
    # account.free
    account.balance = account.balance-cost
    # account.unit_cost = data.get('unit_cost') if data.get('unit_cost')!=None else account.unit_cost
    await account.save()
    return account


@app.post('/recharge-by-manager',description='管理员为其他账号充值')
async def manager_recharge(
    super_user:User=Depends(super_user),
    user_manager:UserManager=Depends(get_user_manager),
    target_email:str=Body(default=None,description='email'),
    amount:decimal.Decimal=Body(default=0,description='充值金额')
):
    try:
        target_user = await user_manager.get_by_email(target_email)
    except UserNotExists:
        raise HTTPException(status_code=400,detail='未找到目标账户')
    account = await Account.find_one(Account.user.id==target_user.id)
    account.balance += amount
    
    return await account.save()



@app.get('/test')
async def test(
    account:Account=Depends(get_account)
):
    print(account.balance)
    return account.balance==decimal.Decimal('0.00')    # 0  0.0 0.00是同一个数字
    
    
@app.on_event("startup")
async def on_startup():
    await init_beanie(
        database=db,
        document_models=[
            Account
        ],
    )
    