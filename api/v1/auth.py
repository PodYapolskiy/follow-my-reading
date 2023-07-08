from datetime import datetime, timedelta
from typing import Annotated, AsyncGenerator
import aioredis
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from config import get_config
from .models import RegisterResponse


config = get_config()


async def get_redis_connection() -> AsyncGenerator[aioredis.Redis, None]:
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

router = APIRouter(prefix="/auth", tags=["auth"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)  # type: ignore


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)  # type: ignore


async def get_user(username: str) -> UserInDB | None:
    async for connection in get_redis_connection():  # async generator syntax
        db: bytes | None = await connection.hget("users", username)
        if not db:
            return None

        return UserInDB.parse_raw(db)
    return None


async def authenticate_user(username: str, password: str) -> UserInDB | None:
    user = await get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(
        to_encode,
        config.token.secket_key,
        algorithm=config.token.jwt_algorithm,
    )
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
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
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
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


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    return current_user


@router.put("/register", response_model=RegisterResponse)
async def register_user(
    username: str,
    password: str,
    conn: Annotated[aioredis.Redis, Depends(get_redis_connection)],
    email: str | None = None,
    full_name: str | None = None,
) -> RegisterResponse:
    hashed_password = get_password_hash(password)
    if await conn.hexists("users", username):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="username is already taken",
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
