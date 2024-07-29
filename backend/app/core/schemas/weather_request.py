from pydantic import BaseModel
from datetime import date, datetime

class WeatherDataCreate(BaseModel):
    zip_code: str
    weather_conditions: str

class WeatherDataResponse(BaseModel):
    id: int
    zip_code: str
    date: date
    timestamp: datetime
    weather_conditions: str

    class Config:
        from_attributes = True
