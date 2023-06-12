from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def index() -> str:
    return "Hello world!"
