from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

# (venv) pip install aiofiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
