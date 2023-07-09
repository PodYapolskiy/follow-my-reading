from datetime import datetime, timedelta
from typing import Annotated, AsyncGenerator

import aioredis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from config import get_config

config = get_config()


async def get_redis_connection() -> AsyncGenerator[aioredis.Redis, None]:
    """
    The function `get_redis_connection` is an asynchronous generator that yields a Redis connection and
    closes it when done.
    """
    connection = aioredis.from_url(config.redis.url, decode_responses=True)
    try:
        yield connection
    finally:
        await connection.close()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    The function `verify_password` checks if a plain password matches a hashed password.

    :param plain_password: The `plain_password` parameter is a string that represents the plain text
    password that needs to be verified
    :type plain_password: str
    :param hashed_password: The `hashed_password` parameter is a string that represents the password
    that has been hashed using a cryptographic algorithm.
    :type hashed_password: str
    :return: a boolean value indicating whether the plain password matches the hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)  # type: ignore


def get_password_hash(password: str) -> str:
    """
    The function `get_password_hash` takes a password as input and returns its hash value.

    :param password: A string representing the password that needs to be hashed
    :type password: str
    :return: a hashed version of the password.
    """
    return pwd_context.hash(password)  # type: ignore


async def get_user(username: str) -> UserInDB | None:
    """
    The function `get_user` retrieves a user from a Redis database by their username and returns it as a
    `UserInDB` object, or `None` if the user does not exist.

    :param username: A string representing the username of the user we want to retrieve from the
    database
    :type username: str
    :return: The function `get_user` returns an instance of `UserInDB` if the user with the specified
    `username` exists in the Redis database. If the user does not exist, it returns `None`.
    """
    async for connection in get_redis_connection():  # async generator syntax
        db: bytes | None = await connection.hget("users", username)
        if not db:
            return None

        return UserInDB.parse_raw(db)
    return None


async def authenticate_user(username: str, password: str) -> UserInDB | None:
    """
    The `authenticate_user` function takes a username and password as input, retrieves the user from the
    database, verifies the password, and returns the user if authentication is successful, otherwise it
    returns None.

    :param username: A string representing the username of the user trying to authenticate
    :type username: str
    :param password: The `password` parameter is a string that represents the password entered by the
    user during the authentication process
    :type password: str
    :return: The function `authenticate_user` returns an instance of `UserInDB` if the user is
    successfully authenticated, or `None` if the user is not found or the password is incorrect.
    """
    user = await get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    The `create_access_token` function generates an access token with an optional expiration time.

    :param data: A dictionary containing the data that you want to encode into the access token. This
    can include any information that you want to associate with the token, such as user ID, roles, or
    permissions
    :type data: dict
    :param expires_delta: The `expires_delta` parameter is an optional argument that specifies the
    duration for which the access token will be valid. It can be a `timedelta` object or `None`. If
    `expires_delta` is `None`, a default expiration time (`config.token.access_exprire_minutes`, or
    30 minutes) will be used
    :type expires_delta: timedelta | None
    :return: an encoded JWT (JSON Web Token) as a string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=config.token.access_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(
        to_encode,
        config.token.secket_key,
        algorithm=config.token.jwt_algorithm,
    )
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    """
    The function `get_current_user` is an asynchronous function that takes a token as input and returns
    the corresponding user if the token is valid.

    :param token: The `token` parameter is a string that represents the authentication token provided by
    the client. It is used to verify the identity of the user making the request
    :type token: Annotated[str, Depends(oauth2_scheme)]
    :return: an instance of the UserInDB class.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            config.token.secket_key,
            algorithms=[config.token.jwt_algorithm],
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    if token_data.username is None:
        raise credentials_exception

    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    The function `get_current_active_user` returns the current user if they are active, otherwise it
    raises an exception.

    :param current_user: The `current_user` parameter is of type `User` and is annotated with
    `Depends(get_current_user)`. This means that the `current_user` parameter is expected to be an
    instance of the `User` class and its value is obtained by calling the `get_current_user` function
    :type current_user: Annotated[User, Depends(get_current_user)]
    :return: the current active user.
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
