
from fastapi import APIRouter, Depends, status, HTTPException, Request, Response, Cookie
import json
import secrets
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from app.core.models.weather_details import WeatherData
from app.core.models.users import User, UserDetails, UserLanguage, Language, UserAllergies, UserHealthConditions, UserMedicalDetails, UserMedications
from app.core.schemas.user_request import CreateUserRequest, LoginRequest, UserDetailsRequest, UserDetailsResponse, LanguageResponse, MedicalDetails, UserMedicalDetailsRequest
from app.core.schemas.weather_request import WeatherDataCreate, WeatherDataResponse
from app.dependencies import db_dependency, get_db, redis_client
from app.services.user_services import get_current_user

weather_router = APIRouter()


@weather_router.post("/add", response_model=WeatherDataResponse)
async def add_weather_data(weather_data: WeatherDataCreate, db: Session = Depends(get_db)):
    current_time = datetime.now()
    new_weather = WeatherData(
        zip_code=weather_data.zip_code,
        date=current_time.date(),
        timestamp=current_time,
        weather_conditions=weather_data.weather_conditions
    )
    db.add(new_weather)
    db.commit()
    db.refresh(new_weather)
    return new_weather

@weather_router.get("/details/{zip_code}", response_model=WeatherDataResponse)
async def get_latest_weather_data(zip_code: str, db: Session = Depends(get_db)):
    latest_weather = db.query(WeatherData).filter(WeatherData.zip_code == zip_code).order_by(WeatherData.timestamp.desc()).first()
    if not latest_weather:
        raise HTTPException(status_code=404, detail="Weather data not found for this zip code")
    return latest_weather