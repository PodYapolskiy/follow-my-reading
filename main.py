import nest_asyncio
from fastapi import FastAPI

from api.v1 import audio_router as audio_router_v1
from api.v1 import image_router as image_router_v1
from api.v1 import task_router as task_router_v1

nest_asyncio.apply()


app = FastAPI()

app.include_router(audio_router_v1, prefix="/v1")
app.include_router(image_router_v1, prefix="/v1")
app.include_router(task_router_v1, prefix="/v1")
