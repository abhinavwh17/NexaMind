from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.files import router as files_router
from app.api.routes.ask import router as ask_router
from app.api.routes.settings import (
    router as settings_router,
)


app = FastAPI(
    title="NexaMind API"
)

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

app.include_router(files_router)
app.include_router(ask_router)
app.include_router(settings_router)

@app.get("/")
def root():
    return {
        "status": "healthy",
        "service": "NexaMind"
    }