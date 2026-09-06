from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.conversation_service import (
    create_conversation,
    delete_conversation,
    get_conversation,
    list_conversations,
    list_messages,
    list_workbook_records,
    update_title,
)
from app.services.dataset_service import clear_dataset, get_dataset

router = APIRouter(prefix="/conversations", tags=["Conversations"])


class RenameConversationRequest(BaseModel):
    title: str


def _detail(conversation_id: str):
    conversation = get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    # Forces a lazy disk restore when the backend has restarted.
    get_dataset(conversation["dataset_id"])
    workbooks = list_workbook_records(conversation_id)
    messages = list_messages(conversation_id)
    return {
        **conversation,
        "workbooks": [
            {
                "workbook_id": item["id"],
                "filename": item["filename"],
            }
            for item in workbooks
        ],
        "messages": messages,
    }


@router.get("")
def conversations_list():
    return {"conversations": list_conversations()}


@router.post("")
def conversations_create():
    return _detail(create_conversation()["id"])


@router.get("/{conversation_id}")
def conversations_get(conversation_id: str):
    return _detail(conversation_id)


@router.patch("/{conversation_id}")
def conversations_rename(conversation_id: str, request: RenameConversationRequest):
    if not get_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    update_title(conversation_id, request.title)
    return _detail(conversation_id)


@router.delete("/{conversation_id}")
def conversations_delete(conversation_id: str):
    conversation = get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    clear_dataset(conversation["dataset_id"])
    delete_conversation(conversation_id)
    return {"deleted": True}
