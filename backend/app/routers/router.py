from fastapi import APIRouter
from .user_routes import user_router
from .user_query_routes import user_query_router
from .weather_data_routes import weather_router

api_router = APIRouter()
api_router.include_router(user_router, prefix="/user", tags=["users"])
api_router.include_router(user_query_router, prefix="/query", tags=["query"])
api_router.include_router(weather_router, prefix="/weather", tags=["weather"])
