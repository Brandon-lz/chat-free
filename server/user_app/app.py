from beanie import init_beanie
from fastapi import Depends, FastAPI,APIRouter

from user_app.db import User, db
from user_app.schemas import UserCreate, UserRead, UserUpdate
from user_app.users import auth_backend, current_active_user, fastapi_users
from fastapi.responses import Response


app = APIRouter()

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth/verify",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
from fastapi import Body,Request
from user_app.users import get_user_manager
from src.redis.config import Redis
from fastapi import HTTPException

@app.post("/auth/verify/verify-bytoken",tags=["auth"])
async def verify_bytoken(request:Request,uuid_token:str=Body(default='xxx-xxx',embed=True),user_manager=Depends(get_user_manager)):
    client = await Redis().create_connection()
    jwt_token = await client.get(name='verify-'+uuid_token)
    if jwt_token==None:
        raise HTTPException(status_code=400,detail='验证已过期，请重新发送验证码')
    
    return await user_manager.verify(jwt_token, request)



@app.get("/auth/jwt/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!","is_verified":user.is_verified}


from .users import get_jwt_strategy


@app.get('/get-jwt',tags=["auth"],description='获取最新的jwt')
async def get_jwt( 
        user :User= Depends(current_active_user)
):
    jwt = await get_jwt_strategy().write_token(user)
    return jwt


    
from user_app.users import refresh_jwt

@app.get('/refresh-login',tags=["auth"],description='刷新jwt，放到返回头里')
async def refresh_login2(
    set_jwt = Depends(refresh_jwt)
):
    return 'in headers'



@app.on_event("startup")
async def on_startup():
    await init_beanie(
        database=db,
        document_models=[
            User,
        ],
    )
    