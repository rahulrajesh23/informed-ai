# from pydantic import BaseModel
# from typing import List, Optional
# from app.database import Base
# from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Date, Text, Float, DateTime

# from sqlalchemy.orm import relationship, sessionmaker


# class Activity(Base):
#     __tablename__ = 'activities'
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     type = Column(String(50))  # e.g., Misc, Health-related, Travel-related
#     description = Column(Text)
#     date = Column(DateTime)
#     duration = Column(Integer)  # Duration in minutes
#     location = Column(String(100))  # Optional

# Activity.user = relationship("User", back_populates="activities")
