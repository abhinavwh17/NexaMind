from fastapi import APIRouter
from pydantic import BaseModel

from app.services.settings_service import (
    save_gemini_key,
    delete_gemini_key,
    is_gemini_key_configured,
)


router = APIRouter(
    prefix="/settings",
    tags=["settings"]
)


class GeminiKeyRequest(BaseModel):
    api_key: str


@router.get("/gemini-status")
def get_gemini_status():
    return {
        "configured":
            is_gemini_key_configured()
    }


@router.post("/gemini-key")
def set_gemini_key(
    request: GeminiKeyRequest
):
    api_key = request.api_key.strip()

    if not api_key:
        return {
            "success": False,
            "message":
                "Gemini API key cannot be empty."
        }

    save_gemini_key(api_key)

    return {
        "success": True
    }


@router.delete("/gemini-key")
def remove_gemini_key():
    delete_gemini_key()

    return {
        "success": True
    }