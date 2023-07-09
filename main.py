import nest_asyncio
from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import from_url

import api.v1
from config import get_config
from core.plugins.no_mem import get_audio_plugins, get_image_plugins

nest_asyncio.apply()


config = get_config()

# acceps no more than 10 request per minute from one user
app = FastAPI(dependencies=[Depends(RateLimiter(times=10, seconds=60))])


@app.on_event("startup")
async def startup() -> None:
    # connect to redis and init limiter
    redis = from_url(
        config.redis.url,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(redis)

    # create directories
    if not config.storage.image_dir.exists():
        config.storage.image_dir.mkdir()

    if not config.storage.audio_dir.exists():
        config.storage.audio_dir.mkdir()

    # wait for atleast one worker to startup by executing lightweight functions
    get_audio_plugins()
    get_image_plugins()


app.include_router(api.v1.router)
