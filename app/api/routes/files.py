from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.excel_service import (
    analyse_excel,
    build_excel_preview,
)
from app.services.dataset_service import (
    create_dataset,
    create_or_replace_dataset,
    get_dataset,
)


router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


SUPPORTED_EXCEL_EXTENSIONS = (".xlsx", ".xls")


def validate_excel_filename(filename: str | None):
    if not filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )

    if not filename.lower().endswith(
        SUPPORTED_EXCEL_EXTENSIONS
    ):
        raise HTTPException(
            status_code=400,
            detail="Only Excel files are supported currently"
        )


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Existing single-file endpoint kept for backward compatibility.
    """
    validate_excel_filename(file.filename)

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


@router.post("/upload-multiple")
async def upload_multiple_files(
    files: list[UploadFile] = File(...),
    dataset_id: str | None = Form(default=None),
):
    """
    Creates or replaces the workbook set in one analysis workspace.

    The frontend sends the complete currently-selected file list whenever
    files are added or removed. Reusing dataset_id keeps the same workspace
    identity while refreshing its workbook catalog.
    """
    if not files:
        raise HTTPException(
            status_code=400,
            detail="At least one Excel file is required"
        )

    if dataset_id and not get_dataset(dataset_id):
        dataset_id = None

    parsed_workbooks = []

    for file in files:
        validate_excel_filename(file.filename)

        content = await file.read()
        sheets = analyse_excel(content)

        parsed_workbooks.append({
            "filename": file.filename,
            "sheets": sheets,
        })

    target_dataset_id = create_or_replace_dataset(
        workbooks=parsed_workbooks,
        dataset_id=dataset_id,
    )

    dataset = get_dataset(target_dataset_id)

    workbook_response = []

    for workbook in dataset.get("workbooks", []):
        workbook_response.append({
            "workbook_id": workbook["workbook_id"],
            "filename": workbook["filename"],
            "sheets": build_excel_preview(
                workbook["sheets"]
            ),
        })

    return {
        "dataset_id": target_dataset_id,
        "status": "processed",
        "workbook_count": len(workbook_response),
        "workbooks": workbook_response,
    }
