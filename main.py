import nest_asyncio
from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from redis.asyncio import from_url

from api.v1 import audio_router as audio_router_v1
from api.v1 import auth_router as auth_router_v1
from api.v1 import image_router as image_router_v1
from api.v1 import task_router as task_router_v1

nest_asyncio.apply()

# acceps no more than 10 request per minute from one user
app = FastAPI(dependencies=[Depends(RateLimiter(times=10, seconds=60))])


@app.on_event("startup")
async def startup():
    redis = from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)


app.include_router(audio_router_v1, prefix="/v1")
app.include_router(image_router_v1, prefix="/v1")
app.include_router(task_router_v1, prefix="/v1")
app.include_router(auth_router_v1, prefix="/v1")
