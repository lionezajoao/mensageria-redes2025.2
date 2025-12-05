# main.py
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.router.routes import router

app = FastAPI()
BASE_DIR = Path(__file__).parent.absolute()

app.include_router(router)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "templates"),
    name="templates",
)

