from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import router as api_router
from app.db import create_job, get_job, init_db
from app.mqtt_client import mqtt_bridge
from app.settings import STATIC_DIR
from app.state import job_queue


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    job_queue.start()
    mqtt_bridge.start(create_job_fn=create_job, get_job_fn=get_job)
    yield
    mqtt_bridge.stop()
    await job_queue.stop()


app = FastAPI(title="Print Gateway", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse(
        {"detail": "UI not built. Run npm install && npm run build in frontend."},
        status_code=404,
    )


@app.get("/{full_path:path}", include_in_schema=False)
def spa_fallback(full_path: str):
    if full_path.startswith("api") or full_path.startswith("static"):
        raise HTTPException(status_code=404, detail="Not found")
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse(
        {"detail": "UI not built. Run npm install && npm run build in frontend."},
        status_code=404,
    )
