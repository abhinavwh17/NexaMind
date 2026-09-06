import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.files import router as files_router
from app.api.routes.ask import router as ask_router
from app.api.routes.settings import router as settings_router
from app.api.routes.conversations import router as conversations_router
from app.services.conversation_service import initialize_database


app = FastAPI(
    title="NexaMind API"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(files_router)
app.include_router(ask_router)
app.include_router(settings_router)
app.include_router(conversations_router)

initialize_database()


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "NexaMind",
    }


def get_frontend_directory():
    if getattr(sys, "frozen", False):
        base_path = Path(
            sys._MEIPASS
        )
    else:
        base_path = (
            Path(__file__)
            .resolve()
            .parent
            .parent
        )

    return (
        base_path
        / "frontend"
        / "dist"
    )


frontend_directory = (
    get_frontend_directory()
)

assets_directory = (
    frontend_directory
    / "assets"
)


if assets_directory.exists():
    app.mount(
        "/assets",
        StaticFiles(
            directory=assets_directory
        ),
        name="assets",
    )


@app.get("/")
def frontend_root():
    return FileResponse(
        frontend_directory
        / "index.html"
    )


@app.get("/{full_path:path}")
def frontend_routes(
    full_path: str,
):
    requested_file = (
        frontend_directory
        / full_path
    )

    if requested_file.exists():
        return FileResponse(
            requested_file
        )

    return FileResponse(
        frontend_directory
        / "index.html"
    )