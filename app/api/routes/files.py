from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.excel_service import (
    analyse_excel,
    build_excel_preview,
)
from app.services.dataset_service import create_dataset


router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )

    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Only Excel files are supported currently"
        )

    content = await file.read()

    sheets = analyse_excel(content)

    dataset_id = create_dataset(
        filename=file.filename,
        sheets=sheets
    )

    preview = build_excel_preview(sheets)

    return {
        "dataset_id": dataset_id,
        "filename": file.filename,
        "status": "processed",
        "sheets": preview
    }