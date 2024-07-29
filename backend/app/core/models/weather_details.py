from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Date, Text, Float, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from app.database import Base

class WeatherData(Base):
    __tablename__ = 'weather_data'

    id = Column(Integer, primary_key=True, index=True)
    zip_code = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    weather_conditions = Column(Text, nullable=False)

    def __init__(self, zip_code, date, timestamp, weather_conditions):
        self.zip_code = zip_code
        self.date = date
        self.timestamp = timestamp
        self.weather_conditions = weather_conditions
