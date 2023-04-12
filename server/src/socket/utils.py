from fastapi import WebSocket, status, Query
from typing import Optional

from ..redis.config import Redis

async def get_token(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):

    if token is None or token == "":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    redis = Redis()
    redis_client = await redis.create_connection()
    isexists = await redis_client.exists(token)

    if isexists == 1:
        return token
    else:
        # 如果令牌超时，用户会话终止，前端可以重新申请令牌
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Session not authenticated or expired token")