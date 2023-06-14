from fastapi import FastAPI
from api.v1 import audio_router as audio_router_v1
from api.v1 import image_router as image_router_v1

app = FastAPI()

app.include_router(audio_router_v1, prefix="/v1")
app.include_router(image_router_v1, prefix="/v1")
