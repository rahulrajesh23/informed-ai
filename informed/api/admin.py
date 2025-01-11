from datetime import datetime
from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy import ColumnElement, select

from informed.db import session_maker
from informed.db_models.users import AccountType, User
from informed.db_models.weather_alert import WeatherAlert
from informed.helper.utils import get_current_user

router = APIRouter()


class WeatherAlertCreate(BaseModel):
    zip_code: str
    message: str
    expires_at: datetime


class WeatherAlertResponse(BaseModel):
    weather_alert_id: UUID
    zip_code: str
    message: str
    created_by: UUID
    created_at: datetime
    expires_at: datetime
    cancelled_at: datetime | None = None
    is_active: bool

    @classmethod
    def from_db(cls, weather_alert: WeatherAlert) -> "WeatherAlertResponse":
        weather_alert_dict = {
            "weather_alert_id": weather_alert.weather_alert_id,
            "zip_code": weather_alert.zip_code,
            "message": weather_alert.message,
            "created_by": weather_alert.created_by,
            "created_at": weather_alert.created_at,
            "expires_at": weather_alert.expires_at,
            "cancelled_at": weather_alert.cancelled_at,
            "is_active": weather_alert.is_active,
        }
        return cls.model_validate(weather_alert_dict)


@router.post("/weather-alerts", response_model=WeatherAlertResponse)
async def create_weather_alert(
    request: Request,
    weather_alert: WeatherAlertCreate,
    current_user: User = Depends(get_current_user),
) -> WeatherAlertResponse:
    if current_user.account_type not in [AccountType.ADMIN, AccountType.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can create weather alerts",
        )

    async with session_maker() as session:
        db_weather_alert = WeatherAlert(
            zip_code=weather_alert.zip_code,
            message=weather_alert.message,
            created_by=current_user.user_id,
            created_at=datetime.now(),
            expires_at=weather_alert.expires_at,
            cancelled_at=None,
            is_active=True,
        )
        session.add(db_weather_alert)
        await session.commit()
        await session.refresh(db_weather_alert)

        # Publish to Redis using app manager
        await request.app.state.app_manager.weather_alert_service.publish_weather_alert(
            db_weather_alert
        )

        return WeatherAlertResponse.from_db(db_weather_alert)


@router.delete("/weather-alerts/{weather_alert_id}")
async def cancel_weather_alert(
    request: Request,
    weather_alert_id: UUID,
    current_user: User = Depends(get_current_user),
) -> None:
    if current_user.account_type not in [AccountType.ADMIN, AccountType.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can cancel weather alerts",
        )

    async with session_maker() as session:
        weather_alert = await session.get(WeatherAlert, weather_alert_id)
        if not weather_alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Weather alert not found",
            )
        weather_alert.cancelled_at = datetime.now()
        weather_alert.is_active = False
        await session.commit()

        # Cancel in Redis using app manager
        await request.app.state.app_manager.weather_alert_service.cancel_weather_alert(
            weather_alert_id, weather_alert.zip_code
        )


@router.get("/weather-alerts", response_model=list[WeatherAlertResponse])
async def list_weather_alerts(
    zip_code: str | None = Query(None, description="Filter by ZIP code"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
) -> list[WeatherAlertResponse]:
    if current_user.account_type not in [AccountType.ADMIN, AccountType.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can list weather alerts",
        )

    async with session_maker() as session:
        query = select(WeatherAlert)

        # Apply filters if provided
        if zip_code is not None:
            query = query.filter(
                cast(ColumnElement[bool], WeatherAlert.zip_code == zip_code)
            )
        if is_active is not None:
            query = query.filter(
                cast(ColumnElement[bool], WeatherAlert.is_active == is_active)
            )

        result = await session.execute(query)
        weather_alerts = result.scalars().all()

        return [WeatherAlertResponse.from_db(n) for n in weather_alerts]
