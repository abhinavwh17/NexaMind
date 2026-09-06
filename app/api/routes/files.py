from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.excel_service import analyse_excel, build_excel_preview
from app.services.dataset_service import create_dataset, create_or_replace_dataset, get_dataset, clear_dataset
from app.services.conversation_service import (
    add_workbooks,
    create_conversation,
    delete_workbook,
    get_conversation,
    get_conversation_by_dataset,
    list_workbook_records,
    replace_workbooks,
)

router = APIRouter(prefix="/files", tags=["Files"])
SUPPORTED_EXCEL_EXTENSIONS = (".xlsx", ".xls")


def validate_excel_filename(filename: str | None):
    if not filename:
        raise HTTPException(status_code=400, detail="No file provided")
    if not filename.lower().endswith(SUPPORTED_EXCEL_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Only Excel files are supported currently")


def _rebuild_persisted_dataset(conversation: dict):
    parsed_workbooks = []
    for record in list_workbook_records(conversation["id"]):
        content = open(record["local_path"], "rb").read()
        parsed_workbooks.append({
            "workbook_id": record["id"],
            "filename": record["filename"],
            "sheets": analyse_excel(content),
        })
    create_or_replace_dataset(parsed_workbooks, dataset_id=conversation["dataset_id"])
    return get_dataset(conversation["dataset_id"])


def _response(conversation: dict):
    dataset = get_dataset(conversation["dataset_id"])
    workbook_response = []
    for workbook in (dataset or {}).get("workbooks", []):
        workbook_response.append({
            "workbook_id": workbook["workbook_id"],
            "filename": workbook["filename"],
            "sheets": build_excel_preview(workbook["sheets"]),
        })
    return {
        "conversation_id": conversation["id"],
        "dataset_id": conversation["dataset_id"],
        "status": "processed",
        "workbook_count": len(workbook_response),
        "workbooks": workbook_response,
    }


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    validate_excel_filename(file.filename)
    content = await file.read()
    sheets = analyse_excel(content)
    dataset_id = create_dataset(filename=file.filename, sheets=sheets)
    return {
        "dataset_id": dataset_id,
        "filename": file.filename,
        "status": "processed",
        "sheets": build_excel_preview(sheets),
    }


@router.post("/upload-multiple")
async def upload_multiple_files(
    files: list[UploadFile] = File(...),
    dataset_id: str | None = Form(default=None),
    conversation_id: str | None = Form(default=None),
    append: bool = Form(default=False),
):
    if not files:
        raise HTTPException(status_code=400, detail="At least one Excel file is required")

    uploaded = []
    for file in files:
        validate_excel_filename(file.filename)
        uploaded.append((file.filename, await file.read()))

    conversation = get_conversation(conversation_id) if conversation_id else None
    if not conversation and dataset_id:
        conversation = get_conversation_by_dataset(dataset_id)
    if not conversation:
        conversation = create_conversation(dataset_id=dataset_id)

    if append:
        add_workbooks(conversation["id"], uploaded)
    else:
        replace_workbooks(conversation["id"], uploaded)

    clear_dataset(conversation["dataset_id"])
    _rebuild_persisted_dataset(conversation)
    return _response(conversation)


@router.delete("/{conversation_id}/{workbook_id}")
def remove_persisted_workbook(conversation_id: str, workbook_id: str):
    conversation = get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if not delete_workbook(conversation_id, workbook_id):
        raise HTTPException(status_code=404, detail="Workbook not found")
    clear_dataset(conversation["dataset_id"])
    _rebuild_persisted_dataset(conversation)
    return _response(conversation)
