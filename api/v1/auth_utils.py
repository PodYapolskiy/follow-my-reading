from datetime import datetime, timedelta
from typing import Annotated, AsyncGenerator
from loguru import logger
import aioredis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from config import get_config

logger.add("./logs/auth_utils.log", format="{time:DD-MM-YYYY HH:mm:ss zz} {level} {message}", enqueue=True)

config = get_config()


async def get_redis_connection() -> AsyncGenerator[aioredis.Redis, None]:
    """
    The function `get_redis_connection` is an asynchronous generator that yields a Redis connection and
    closes it when done.
    """
    logger.info("Starting get_redis_connection algorithm. Connecting to database.")
    connection = aioredis.from_url(config.redis.url, decode_responses=True)
    try:
        logger.info("Yielding connection.")
        yield connection
    finally:
        logger.info("Closing connection.")
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
    logger.info("Starting verify_password algorithm. Verifying password.")
    return pwd_context.verify(plain_password, hashed_password)  # type: ignore


def get_password_hash(password: str) -> str:
    """
    The function `get_password_hash` takes a password as input and returns its hash value.

    :param password: A string representing the password that needs to be hashed
    :type password: str
    :return: a hashed version of the password.
    """
    logger.info("Starting get_password_hash algorithm. Returning hashed password.")
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
    logger.info("Starting get_user algorithm.")
    async for connection in get_redis_connection():  # async generator syntax
        logger.info("Searching user in the database")
        db: bytes | None = await connection.hget("users", username)
        if not db:
            logger.info("Username does not exist in the database. Returning None value.")
            return None

        logger.info("Username was found. Returning a user instance.")
        return UserInDB.parse_raw(db)
    logger.error("Failed too connect to the database. Returning None value.")
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
    logger.info("Starting authenticate_user algorithm. Getting user instance.\n"
                "For more info check api/v1/logs/auth_utils.log\n"
                "Process: get_user")
    user = await get_user(username)

    logger.info("Checking if user exists in database.")
    if not user:
        logger.info("User does not exist in database. Returning None value.")
        return None

    logger.info("User exists in database. Checking if password is correct.")
    if not verify_password(password, user.hashed_password):
        logger.info("Password of the user is incorrect. Returning None value.")
        return None

    logger.info("User has been successfully authenticated. Returning user instance.")
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
    `expires_delta` is `None`, a default expiration time (`config.token.access_expire_minutes`, or
    30 minutes) will be used
    :type expires_delta: timedelta | None
    :return: an encoded JWT (JSON Web Token) as a string.
    """
    logger.info("Starting create_access_token algorithm. Acquiring data.")
    to_encode = data.copy()

    logger.info("Checking if the custom duration of access token was specified.")
    if expires_delta:
        logger.info(f"Custom duration of access token was specified. Setting duration to ({expires_delta}) minutes.")
        expire = datetime.utcnow() + expires_delta
    else:
        logger.info(f"Custom duration of access token was not specified. Setting duration to "
                    f"({config.token.access_expire_minutes}) minutes")
        expire = datetime.utcnow() + timedelta(
            minutes=config.token.access_expire_minutes
        )

    logger.info("Adding expiration date to the data.")
    to_encode.update({"exp": expire})

    logger.info("Encoding data.")
    encoded_jwt: str = jwt.encode(
        to_encode,
        config.token.secket_key,
        algorithm=config.token.jwt_algorithm,
    )

    logger.info("Returning encoded data.")
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
    logger.info("Starting get_current_user algorithm. Acquiring encoded data.")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.info("Decoding data.")
        payload = jwt.decode(
            token,
            config.token.secket_key,
            algorithms=[config.token.jwt_algorithm],
        )

        logger.info("Acquiring username from the decoded data.")
        username: str = payload.get("sub")

        if username is None:
            logger.error("Username is not found. Raising 401 file error.")
            raise credentials_exception

        logger.info("Creating token data for the user.")
        token_data = TokenData(username=username)
    except JWTError:
        logger.error("Decoding failed. Raising 401 file error.")
        raise credentials_exception

    logger.info("Checking if the username for the token exists")
    if token_data.username is None:
        raise credentials_exception

    logger.info("Acquiring user data.\n"
                "for more info check api/v1/logs/auth_utils.log\n"
                "Process: get_user")
    user = await get_user(username=token_data.username)

    if user is None:
        logger.error("User was not found. Raising 401 file error.")
        raise credentials_exception

    logger.info("Access token has been created successfully. Returning user instance.")
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

    logger.info("Starting get_current_active_user algorithm. Checking if user is disabled.")
    if current_user.disabled:
        logger.error("User is disabled. Raising 400 file error.")
        raise HTTPException(status_code=400, detail="Inactive user")

    logger.info("User is active. Returning current user instance.")
    return current_user
