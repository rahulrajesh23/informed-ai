import json
import secrets
import traceback
from typing import cast

from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import ColumnElement, select
from sqlalchemy.exc import IntegrityError

from informed.api.schema import (
    AuthenticatedUserResponse,
    CreateUserRequest,
    LoginRequest,
    SettingsRequest,
    SettingsResponse,
    UserDetailsRequest,
    UserDetailsResponse,
    UserMedicalDetailsRequest,
    UserMedicalDetailsResponse,
)
from informed.db import session_maker
from informed.db_models.users import (
    AccountType,
    Settings,
    User,
    UserConfigurations,
    UserDetails,
    UserHealthConditions,
    UserMedicalDetails,
    UserMedications,
    WeatherSensitivities,
)
from informed.helper.utils import UserDep

router = APIRouter()


async def set_session_cookie(request: Request, response: Response, user: User) -> None:
    redis_client = request.app.state.redis_client
    session_token = secrets.token_urlsafe()
    session_object = {"email": user.email, "role": "admin"}
    serialized_session = json.dumps(session_object)
    await redis_client.set(session_token, serialized_session, ex=3600)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )


@router.post(
    "/register",
    response_model=AuthenticatedUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user: CreateUserRequest, request: Request, response: Response
) -> AuthenticatedUserResponse:
    try:
        async with session_maker() as session:
            new_user = User(
                email=user.email,
                is_active=True,
                account_type=AccountType.USER,
            )
            new_user.details = UserDetails(
                user_id=new_user.user_id,
                first_name=user.first_name,
                last_name=user.last_name,
            )
            new_user.medical_details = UserMedicalDetails.create(
                user_id=new_user.user_id
            )
            new_user.settings = Settings(
                user_id=new_user.user_id,
                configurations=UserConfigurations(),
            )

            session.add(new_user)
            try:
                await session.commit()
                await set_session_cookie(request, response, new_user)
                return AuthenticatedUserResponse.from_user(new_user)
            except IntegrityError as ie:
                await session.rollback()
                if "users_email_key" in str(ie):
                    raise HTTPException(status_code=400, detail="Email already exists")
                else:
                    print(f"Unexpected IntegrityError: {ie!s}")
                    raise HTTPException(
                        status_code=500, detail="An unexpected database error occurred"
                    )
    except Exception as e:
        print(f"Unexpected error in register_user: {e!s}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while registering the user",
        )


@router.post("/login", response_model=AuthenticatedUserResponse)
async def login(
    request: Request, login_request: LoginRequest, response: Response
) -> AuthenticatedUserResponse:

    try:
        async with session_maker() as session:
            result = await session.execute(
                select(User).filter(
                    cast(ColumnElement[bool], User.email == login_request.email)
                )
            )
            db_user = result.unique().scalar_one_or_none()
            if db_user:

                await set_session_cookie(request, response, db_user)
                return AuthenticatedUserResponse.from_user(db_user)
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e!s}")


@router.get("/logout")
async def logout(request: Request, response: Response) -> dict:
    session_token = request.cookies.get("session_token")
    redis_client = request.app.state.redis_client
    if session_token:
        await redis_client.delete(session_token)
        return {"message": "Logged out"}
    raise HTTPException(status_code=400, detail="No active session found")


@router.get("/me")
async def check_session_alive(
    current_user: UserDep,
) -> AuthenticatedUserResponse:
    try:
        return AuthenticatedUserResponse.from_user(user=current_user)
    except Exception:
        raise HTTPException(status_code=400, detail="No active session found")


@router.post("/details", response_model=UserDetailsResponse)
async def set_user_details(
    details: UserDetailsRequest,
    current_user: UserDep,
) -> UserDetailsResponse:
    async with session_maker() as session:
        user = current_user
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.details:
            user.details = UserDetails(
                user_id=user.user_id,
                first_name=details.first_name,
                last_name=details.last_name,
            )

        user.details.first_name = details.first_name
        user.details.last_name = details.last_name
        user.details.age = details.age
        user.details.address_line1 = details.address_line1
        user.details.address_line2 = details.address_line2
        user.details.city = details.city
        user.details.state = details.state
        user.details.zip_code = details.zip_code
        user.details.country = details.country
        user.details.phone_number = details.phone_number
        user.details.ethnicity = details.ethnicity
        user.details.language = details.language
        session.add(user.details)

        try:
            await session.commit()
            await session.flush()
        except IntegrityError as e:
            await session.rollback()
            print(f"IntegrityError: {e!s}")
            raise HTTPException(
                status_code=500, detail="An error occurred while updating user details"
            )

    return UserDetailsResponse.from_user_details(user.details)


@router.get("/details", response_model=UserDetailsResponse)
async def get_user_details(
    current_user: UserDep,
) -> UserDetailsResponse:

    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.details:
        raise HTTPException(status_code=404, detail="User details not found")

    return UserDetailsResponse.from_user_details(user.details)


@router.get("/medical-details", response_model=UserMedicalDetailsResponse)
async def get_medical_details(
    current_user: UserDep,
) -> UserMedicalDetailsResponse:

    user = current_user
    if not user.medical_details:
        raise HTTPException(status_code=404, detail="Medical details not found")

    return UserMedicalDetailsResponse.from_user_medical_details(user.medical_details)


@router.post("/medical-details", response_model=UserMedicalDetailsResponse)
async def set_medical_details(
    details: UserMedicalDetailsRequest,
    current_user: UserDep,
) -> UserMedicalDetailsResponse:
    user = current_user
    try:
        async with session_maker() as session:
            if user.medical_details:
                medical_details = user.medical_details
            else:
                medical_details = UserMedicalDetails(user_id=user.user_id)

            medical_details.blood_type = details.blood_type
            medical_details.height = details.height
            medical_details.weight = details.weight

            # Handle health conditions
            medical_details.health_conditions = []
            for condition in details.health_conditions:
                health_condition = UserHealthConditions(
                    user_medical_id=medical_details.id,
                    condition=condition.condition,
                    severity=condition.severity,
                    description=condition.description,
                )
                medical_details.health_conditions.append(health_condition)

            # Handle medications
            medical_details.medications = []
            for med in details.medications:
                medication = UserMedications(
                    user_medical_id=medical_details.id,
                    name=med.name,
                    dosage=med.dosage,
                    frequency=med.frequency,
                )
                medical_details.medications.append(medication)

            # Handle weather sensitivities
            medical_details.weather_sensitivities = []
            for sensitivity in details.weather_sensitivities:
                weather_sensitivity = WeatherSensitivities(
                    user_medical_id=medical_details.id,
                    type=sensitivity.type,
                    description=sensitivity.description,
                )
                medical_details.weather_sensitivities.append(weather_sensitivity)

            user.medical_details = medical_details
            session.add(user)
            await session.commit()
            return UserMedicalDetailsResponse.from_user_medical_details(medical_details)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e!s}"
        )


@router.get("/settings")
async def get_settings(user: UserDep) -> SettingsResponse:
    return SettingsResponse.from_user_settings(user.settings)


@router.post("/settings")
async def set_settings(settings: SettingsRequest, user: UserDep) -> SettingsResponse:
    try:
        async with session_maker() as session:
            user.settings.configurations = settings.to_user_configurations()
            session.add(user)
            await session.commit()
            return SettingsResponse.from_user_settings(user.settings)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e!s}"
        )
