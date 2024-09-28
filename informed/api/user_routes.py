from fastapi import APIRouter, Depends, status, HTTPException, Request, Response, Cookie
import json
import secrets
import traceback
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from informed.db_models.users import User, UserDetails, UserLanguage, Language, UserAllergies, UserHealthConditions, UserMedicalDetails, UserMedications
from informed.api.types import CreateUserRequest, LoginRequest, UserDetailsRequest, UserDetailsResponse, UserMedicalDetailsRequest
from backend.app.dependencies import redis_client
from backend.app.services.user_services import get_current_user
from sqlalchemy import select, ColumnElement, delete
from informed.db import session_maker
from typing import cast

user_router = APIRouter()


from sqlalchemy.exc import IntegrityError
import traceback

@user_router.post("/register", response_model=CreateUserRequest, status_code=status.HTTP_201_CREATED)
async def register_user(user: CreateUserRequest, request: Request):
    try:
        async with session_maker() as session:
            # Check if user with the same username or email already exists
            existing_user = await session.execute(
                select(User).filter(
                    (User.username == user.username) | (User.email == user.email)
                )
            )
            if existing_user.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Username or email already exists")

            new_user = User(username=user.username, email=user.email, is_active=True, account_type="user")
            session.add(new_user)
            try:
                await session.commit()
                return CreateUserRequest(username=new_user.username, email=new_user.email)
            except IntegrityError as ie:
                await session.rollback()
                if "users_email_key" in str(ie):
                    raise HTTPException(status_code=400, detail="Email already exists")
                elif "users_username_key" in str(ie):
                    raise HTTPException(status_code=400, detail="Username already exists")
                else:
                    print(f"Unexpected IntegrityError: {str(ie)}")
                    raise HTTPException(status_code=500, detail="An unexpected database error occurred")
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        print(f"Unexpected error in register_user: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while registering the user")


@user_router.post("/set-user-details/{username}")
async def set_user_details(username: str, details: UserDetailsRequest, current_user: User = Depends(get_current_user)):
    if not current_user or (current_user.username != username and current_user.account_type != "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user's details")

    async with session_maker() as session:
        # Check if the user exists
        user = current_user
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Handle the user details
        if not user.details:
            user.details = UserDetails(user_id=user.id)
             
        
        # Update user details
        for field in UserDetails.__table__.columns:
            if field.name in details.__dict__ and field.name not in ['id', 'user_id']:
                setattr(user.details, field.name, getattr(details, field.name))
        session.add(user.details)
        

        # Clear existing languages
        await session.execute(delete(UserLanguage).where(UserLanguage.user_details_id == user.details.id))
        
        # Add new languages
        for lang in details.languages:
            user_lang = UserLanguage(user_details_id=user.details.id, **lang.model_dump())
            session.add(user_lang)

        try:
            await session.commit()
            await session.flush()
        except IntegrityError as e:
            await session.rollback()
            print(f"IntegrityError: {str(e)}")
            raise HTTPException(status_code=500, detail="An error occurred while updating user details")

    return {"message": "User details updated successfully"}

@user_router.get("/get-user-details/{username}")
async def get_user_details(username: str, current_user: User = Depends(get_current_user)):

    if not current_user or current_user.username != username and current_user.account_type != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user's details")

    # Fetch user by username including details and languages
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.details:
        raise HTTPException(status_code=404, detail="User details not found")

    # Construct the response
    return user.details.model_dump(mode='json')



@user_router.get("/{username}/medical-details", response_model=UserMedicalDetails)
async def get_medical_details(username: str, current_user: User = Depends(get_current_user)):

    if not current_user or current_user.username != username and current_user.account_type != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user's details")
    
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.medical_details.model_dump(mode='json')


@user_router.post("/{username}/medical-details")
async def set_medical_details(username: str, details: UserMedicalDetailsRequest, current_user: User = Depends(get_current_user)):
    if not current_user or current_user.username != username and current_user.account_type != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user's details")
    
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        async with session_maker() as session:
            # Update or create medical details
            if user.medical_details:
                medical_details = user.medical_details
            else:
                medical_details = UserMedicalDetails(user_id=user.id)
                # db.add(medical_details)

            medical_details.blood_type = details.blood_type
            medical_details.height = details.height
            medical_details.weight = details.weight

            # Handle health conditions
            medical_details.health_conditions = []
            for condition in details.health_conditions:
                health_condition = UserHealthConditions(
                    user_medical_id=medical_details.id,
                    condition=condition['condition'],
                    severity=condition['severity'],
                    description=condition.get('description')
                )
                medical_details.health_conditions.append(health_condition)

            # Handle medications
            medical_details.medications = []
            for med in details.medications:
                medication = UserMedications(
                    user_medical_id=medical_details.id,
                    name=med['name'],
                    dosage=med['dosage'],
                    frequency=med['frequency']
                )
                medical_details.medications.append(medication)

            user.medical_details = medical_details
            session.add(user)
            await session.commit()
            return {"message": "Medical details updated successfully"}
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@user_router.post("/login")
async def login(login_request: LoginRequest, response: Response):
    try:
        async with session_maker() as session:
            result = await session.execute(
                select(User).filter(User.username == login_request.username)
            )
            db_user = result.unique().scalar_one_or_none()
            if db_user:
                session_token = secrets.token_urlsafe()
                session_object = {
                    "username": login_request.username,
                    "role": "admin"
                }
                serialized_session = json.dumps(session_object)
                redis_client.set(session_token, serialized_session, ex=3600)  # Store session with 1-hour expiration
                response.set_cookie(key="session_token", value=session_token, httponly=True, secure=True, samesite='Lax')
                return {"data": db_user, "message": "Login Successful"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username"
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@user_router.get("/me")
async def read_users_me(request: Request, current_user: User = Depends(get_current_user)):
    try:
        if current_user:
            # TODO: Don't return Medical Details
            return {"data": current_user, 'sessionAlive': True, "message": "Login Successful"}
        # else:
        #     return {'sessionAlive': False, "message": "No Session Found"}
    except Exception as e:
        raise e

@user_router.get("/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        redis_client.delete(session_token)
        response.delete_cookie("session_token")
        return {"message": "Logged out"}
    raise HTTPException(status_code=400, detail="No active session found")