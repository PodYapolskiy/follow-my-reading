from datetime import timedelta
from typing import Annotated
from loguru import logger
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

logger.add(
    "./logs/auth.log",
    format="{time:DD-MM-YYYY, HH:mm:ss zz} {level} {message}",
    enqueue=True,
)

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
    logger.info("Starting register_user algorithm. Hashing password.")
    hashed_password = get_password_hash(password)

    logger.info("Password hashed. Checking if username already exists in database.")
    if await conn.hexists("users", username):
        logger.error("The username is already taken. Raising 422 file error.")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username is already taken",
        )

    logger.info("Username is valid. Encoding data and adding to database.")
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

    logger.info("A user has registered in database successfully.")
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
    logger.info("Starting login_for_access_token algorithm. Acquiring user data.")
    user = await authenticate_user(form_data.username, form_data.password)

    logger.info("Checking correctness of login information.")
    if not user:
        logger.error("Incorrect username or password. Raising 401 file error.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("Login information is correct. Creating 30 minutes access token.")
    access_token_expires = timedelta(minutes=config.token.access_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    logger.info("Access token is successfully created. Returning the token.")
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
    logger.info("Starting read_users_me algorithm.")
    return current_user
