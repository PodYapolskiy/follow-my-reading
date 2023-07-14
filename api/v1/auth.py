from datetime import timedelta
from typing import Annotated

import aioredis
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from config import get_config

from .auth_utils import (
    Token,
    User,
    UserInDB,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    get_redis_connection,
)
from .models import RegisterResponse

config = get_config()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.put(
    "/register",
    response_model=RegisterResponse,
    status_code=200,
    summary="""The endpoint `/register` registers a new user by storing their username, password, email, and
    full name in a Redis database.""",
    responses={
        422: {
            "description": "The specified username is already taken",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Username is already taken",
                    }
                }
            },
        },
    },
)
async def register_user(
    username: str,
    password: str,
    conn: Annotated[aioredis.Redis, Depends(get_redis_connection)],
    email: str | None = None,
    full_name: str | None = None,
) -> RegisterResponse:
    """
    Parameters:
    - **username**: The "username: parameter is a string representing the username of the user being registered
    - **password**: The "password" parameter is a string that represents the user's password
    - **email**: The "email" parameter is an optional string that represents the email address of the user
    - **full_name**: The "full_name" parameter is an optional parameter that represents the full name of the user
    """
    hashed_password = get_password_hash(password)
    if await conn.hexists("users", username):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username is already taken",
        )
    encoded_data = UserInDB.json(
        UserInDB(
            username=username,
            email=email,
            full_name=full_name,
            disabled=False,
            hashed_password=hashed_password,
        )
    )
    await conn.hset("users", username, encoded_data)
    return RegisterResponse(text="Registered successfully.")


@router.post(
    "/token",
    response_model=Token,
    status_code=200,
    summary="""The endpoint `/token` handles the login process and returns an
access token for the authenticated user.""",
    responses={
        401: {
            "description": "Incorrect username or password.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Incorrect username or password",
                    }
                }
            },
        },
    },
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    Parameters:
    - **username** - unique username, which the client has provided while registering
    - **password** - client's password

    Responses:
    - 401, incorrect username or password
    - 200, token
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.token.access_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/users/me",
    response_model=User,
    status_code=200,
    summary="""The endpoint `/users/me` returns the current user.""",
    responses={
        400: {
            "description": "User is inactive",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Inactive user",
                    }
                }
            },
        },
        401: {
            "description": "Could not validate credentials",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Could not validate credentials",
                    }
                }
            },
        },
    },
)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    return current_user
