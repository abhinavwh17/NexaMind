import uuid

from app.services.excel_service import analyse_excel
from app.services.conversation_service import (
    get_conversation_by_dataset,
    list_workbook_records,
)

# Runtime cache only. Durable copies live on disk and can rebuild this cache.
datasets = {}


def _create_workbook_entry(filename: str, sheets: dict, workbook_id: str | None = None):
    return {
        "workbook_id": workbook_id or str(uuid.uuid4()),
        "filename": filename,
        "sheets": sheets,
    }


def create_dataset(filename: str, sheets: dict):
    return create_or_replace_dataset(workbooks=[{"filename": filename, "sheets": sheets}])


def create_or_replace_dataset(workbooks: list[dict], dataset_id: str | None = None):
    target_dataset_id = dataset_id or str(uuid.uuid4())
    entries = []
    for workbook in workbooks:
        entries.append(
            _create_workbook_entry(
                filename=workbook["filename"],
                sheets=workbook["sheets"],
                workbook_id=workbook.get("workbook_id"),
            )
        )
    datasets[target_dataset_id] = {"workbooks": entries}
    return target_dataset_id


def restore_dataset(dataset_id: str):
    conversation = get_conversation_by_dataset(dataset_id)
    if not conversation:
        return None
    workbooks = []
    for record in list_workbook_records(conversation["id"]):
        try:
            content = open(record["local_path"], "rb").read()
            sheets = analyse_excel(content)
        except FileNotFoundError:
            continue
        workbooks.append({
            "workbook_id": record["id"],
            "filename": record["filename"],
            "sheets": sheets,
        })
    return create_or_replace_dataset(workbooks, dataset_id=dataset_id) and datasets[dataset_id]


def get_dataset(dataset_id: str):
    dataset = datasets.get(dataset_id)
    if dataset is not None:
        return dataset
    return restore_dataset(dataset_id)


def clear_dataset(dataset_id: str):
    datasets.pop(dataset_id, None)


def get_workbook(dataset: dict, workbook_id: str):
    for workbook in dataset.get("workbooks", []):
        if workbook.get("workbook_id") == workbook_id:
            return workbook
    return None


def get_workbooks(dataset: dict):
    return dataset.get("workbooks", [])
