from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import initialize_database
from app.tasks import router as tasks_router

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "static"

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(title="Task Tracker", lifespan=lifespan)
app.include_router(tasks_router)
app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)

@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/")
def home() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")