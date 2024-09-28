from fastapi import APIRouter, status, HTTPException, Cookie
from sqlalchemy.future import select
import json
from backend.app.dependencies import redis_client
from informed.db_models.users import User
from informed.db import session_maker
from typing import Any
async def get_current_user(session_token: str = Cookie(None)):
    if session_token is None:
        return None
    
    serialized_session = redis_client.get(session_token)
    if not serialized_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session or expired session")
    
    session_object = json.loads(serialized_session)
    if not session_object or not session_object.get("username"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session data")
    
    try:
        async with session_maker() as session:
            result = await session.execute(
                select(User).filter(User.username == session_object["username"])
            )
            user = result.unique().scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

user_router = APIRouter()