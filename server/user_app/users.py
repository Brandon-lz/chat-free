from typing import Optional

from beanie import PydanticObjectId
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
from fastapi.responses import Response


from user_app.db import User, get_user_db

from src.email.email_send import send_email
import json
from src.redis.config import Redis
import uuid
from account_app.db import Account
import decimal

from logs import logger

redis = Redis()

SECRET = "SECRETkajdflj"


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    verification_token_lifetime_seconds = 60*60*12

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.info(f"User {user.id} has registered.")
        try:
            account = await Account(user=user.id,balance=decimal.Decimal('0.0')).create()
        except Exception as err:
            logger.error('user_id:'+str(user.id)+'\n error info:\n'+str(err))
        logger.info(f'create account to user:{user.id}:{account.json()}')

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        # expire_time = 
        # token = user_jwt(expire_time).write_token(user)
        client = await redis.create_connection()
        uuid_str = str(uuid.uuid4())
        await client.setex('verify-'+uuid_str,time=self.verification_token_lifetime_seconds-60,value=token)
        send_email(receiver=user.email,url=f'http://dbt-dev.natapp1.cc/verify/{uuid_str}')
        logger.info(f"Verification requested for user {user.email}. Verification token: {token}. key: {uuid_str}")

    # 自定义类方法
    async def validate_password(self, password: str, user:User) -> None:
        return await super().validate_password(password, user)

async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=60*60*3)

def user_jwt(expire:int=60*60*12)-> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=expire)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, PydanticObjectId](get_user_manager, [auth_backend])

# 鉴权用户类型定义：
current_active_user = fastapi_users.current_user(active=True)
user_or_not = fastapi_users.current_user(optional=True)
super_user = fastapi_users.current_user(superuser=True,verified=True,active=True)


# jwt tools 
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt



async def refresh_jwt(   
    response:Response,
    user:User=Depends(user_or_not)
):
    """刷新jwt的Depends，会将新的jwt放到返回头里

    Args:
        response (Response): _description_
        user (User, optional): _description_. Defaults to Depends(current_active_user).

    Returns:
        _type_: _description_
    """
    if user!=None:
        jwt = await get_jwt_strategy().write_token(user)
        response.headers.update({'Bearer':jwt})
        return jwt
    return None