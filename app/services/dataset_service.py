import uuid


# Temporary in-memory storage.
# A dataset now represents one analysis workspace that may contain
# one or more Excel workbooks.
datasets = {}


def _create_workbook_entry(filename: str, sheets: dict):
    return {
        "workbook_id": str(uuid.uuid4()),
        "filename": filename,
        "sheets": sheets,
    }


def create_dataset(filename: str, sheets: dict):
    """
    Backward-compatible helper for a single workbook.
    """
    return create_or_replace_dataset(
        workbooks=[
            {
                "filename": filename,
                "sheets": sheets,
            }
        ]
    )


def create_or_replace_dataset(
    workbooks: list[dict],
    dataset_id: str | None = None,
):
    """
    Create a new analysis workspace, or replace the workbooks inside an
    existing workspace while keeping the same dataset_id.

    Each workbook gets its own internal workbook_id so duplicate filenames
    are safe and the LLM can reference a specific workbook without relying
    on the filename as an identifier.
    """
    if dataset_id and dataset_id in datasets:
        target_dataset_id = dataset_id
    else:
        target_dataset_id = str(uuid.uuid4())

    workbook_entries = []

    for workbook in workbooks:
        workbook_entries.append(
            _create_workbook_entry(
                filename=workbook["filename"],
                sheets=workbook["sheets"],
            )
        )

    datasets[target_dataset_id] = {
        "workbooks": workbook_entries,
    }

    return target_dataset_id


def get_dataset(dataset_id: str):
    return datasets.get(dataset_id)


def get_workbook(dataset: dict, workbook_id: str):
    for workbook in dataset.get("workbooks", []):
        if workbook.get("workbook_id") == workbook_id:
            return workbook

    return None


def get_workbooks(dataset: dict):
    return dataset.get("workbooks", [])
