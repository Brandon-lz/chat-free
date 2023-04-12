from fastapi import FastAPI
import uvicorn
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from routes.chat import chat
from user_app.app import app
from account_app.app import app as acapp


load_dotenv()

api = FastAPI()
api.include_router(chat)
api.include_router(app)
api.include_router(acapp)

# 允许的origin
origins = [
    "*"
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.get("/test")
async def root():
    return {"msg": "API is Online"}



if __name__ == "__main__":
    if os.environ.get('APP_ENV') == "development":
        uvicorn.run(
            "main:api", 
            host="0.0.0.0", 
            port=int(os.environ['SERVER_PORT']),
            # port=8093,
            workers=4, 
            reload=True,
            log_level='info',
        )
    else:
        print(1111111)


