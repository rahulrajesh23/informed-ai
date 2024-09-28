from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, String, Boolean, Integer, Text, Float, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid as SQLAlchemyUuid
from datetime import datetime
from enum import Enum

class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(sa_column=Column(String(50), unique=True, nullable=False))
    email: str = Field(sa_column=Column(String(100), unique=True, nullable=False))
    is_active: bool = Field(sa_column=Column(Boolean))
    account_type: str = Field(sa_column=Column(String))

    details: Optional["UserDetails"] = Relationship(
        sa_relationship=relationship(
            "UserDetails",
            back_populates="user",
            lazy="joined",  # Set lazy loading here
            passive_deletes="all",
        )
    )
    activities: List["Activity"] = Relationship(
        sa_relationship=relationship(
            "Activity",
            back_populates="user",
            lazy="joined",  # Set lazy loading here
            passive_deletes="all",
        )
    )
    medical_details: Optional["UserMedicalDetails"] = Relationship(
        sa_relationship=relationship(
            "UserMedicalDetails",
            back_populates="user",
            lazy="joined",  # Set lazy loading here
            passive_deletes="all",
        )
    )

    

class Activity(SQLModel, table=True):
    __tablename__ = 'activities'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False
        )
    )
    type: str = Field(sa_column=Column(String(50)))
    description: str = Field(sa_column=Column(Text))
    date: datetime = Field(sa_column=Column(DateTime))
    duration: int
    location: Optional[str] = Field(sa_column=Column(String(100)))
    user: "User" = Relationship(
        sa_relationship=relationship(
            "User",
            back_populates="activities",
            lazy="joined",  # Set lazy loading here
        )
    )

class UserDetails(SQLModel, table=True):
    __tablename__ = 'user_details'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True
        )
    )
    first_name: str = Field(sa_column=Column(String(100), nullable=False))
    last_name: str = Field(sa_column=Column(String(100), nullable=False))
    age: Optional[int] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = Field(sa_column=Column(String(50)))
    state: Optional[str] = Field(sa_column=Column(String(30)))
    zip_code: Optional[str] = Field(sa_column=Column(String(20)))
    country: Optional[str] = Field(sa_column=Column(String(50)))
    phone_number: Optional[str] = None
    ethnicity: Optional[str] = None
    languages: List["UserLanguage"] = Relationship(
        sa_relationship=relationship(
            "UserLanguage",
            back_populates="user_details",
            lazy="joined",  # Set lazy loading here
            passive_deletes="all"
        )
    )
    user: "User" = Relationship(
        sa_relationship=relationship(
            "User",
            back_populates="details",
            lazy="joined",  # Set lazy loading here
        )
    )

class Language(str, Enum):
    ENGLISH = "english"
    SPANISH = "spanish"
    # Add more languages as needed

class UserLanguage(SQLModel, table=True):
    __tablename__ = 'user_languages'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_details_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("user_details.id", ondelete="CASCADE"),
            nullable=False
        )
    )
    is_preferred: bool = Field(default=False, nullable=False)
    name: Language = Field(sa_column=Column(SQLAlchemyEnum(Language)))
    user_details: "UserDetails" = Relationship(
        sa_relationship=relationship(
            "UserDetails",
            back_populates="languages",
            lazy="joined",  # Set lazy loading here
        )
    )

class UserMedicalDetails(SQLModel, table=True):
    __tablename__ = 'user_medical_details'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True
        )
    )
    blood_type: Optional[str] = Field(sa_column=Column(String(3)))
    height: Optional[float] = None
    weight: Optional[float] = None
    user: "User" = Relationship(
        sa_relationship=relationship(
            "User",
            back_populates="medical_details",
            lazy="joined",  # Set lazy loading here
        )
    )
    health_conditions: List["UserHealthConditions"] = Relationship(
        sa_relationship=relationship(
            "UserHealthConditions",
            back_populates="user_medical_details",
            lazy="joined",  # Set lazy loading here
            passive_deletes="all"
        )
    )
    medications: List["UserMedications"] = Relationship(
        sa_relationship=relationship(
            "UserMedications",
            back_populates="user_medical_details",
            lazy="joined",  # Set lazy loading here
            passive_deletes="all"
        )
    )
    allergies: List["UserAllergies"] = Relationship(
        sa_relationship=relationship(
            "UserAllergies",
            back_populates="user_medical_details",
            lazy="joined",  # Set lazy loading here
            passive_deletes="all"
        )
    )

class UserHealthConditions(SQLModel, table=True):
    __tablename__ = 'user_health_conditions'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_medical_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("user_medical_details.id", ondelete="CASCADE")
        )
    )
    condition: str = Field(sa_column=Column(String(100)))
    severity: str = Field(sa_column=Column(String(50)))
    description: Optional[str] = Field(sa_column=Column(Text))
    user_medical_details: "UserMedicalDetails" = Relationship(
        sa_relationship=relationship(
            "UserMedicalDetails",
            back_populates="health_conditions",
            lazy="joined",  # Set lazy loading here
        )
    )

class UserMedications(SQLModel, table=True):
    __tablename__ = 'user_medications'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_medical_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("user_medical_details.id", ondelete="CASCADE")
        )
    )
    name: str = Field(sa_column=Column(String(100)))
    dosage: str = Field(sa_column=Column(String(100)))
    frequency: str = Field(sa_column=Column(String(50)))
    user_medical_details: "UserMedicalDetails" = Relationship(
        sa_relationship=relationship(
            "UserMedicalDetails",
            back_populates="medications",
            lazy="joined",  # Set lazy loading here
        )
    )

class UserAllergies(SQLModel, table=True):
    __tablename__ = 'user_allergies'
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_medical_id: UUID = Field(
        sa_column=Column(
            SQLAlchemyUuid(as_uuid=True),
            ForeignKey("user_medical_details.id", ondelete="CASCADE")
        )
    )
    allergen: str = Field(sa_column=Column(String(100)))
    reaction: Optional[str] = Field(sa_column=Column(Text))
    user_medical_details: "UserMedicalDetails" = Relationship(
        sa_relationship=relationship(
            "UserMedicalDetails",
            back_populates="allergies",
            lazy="joined",  # Set lazy loading here
        )
    )
