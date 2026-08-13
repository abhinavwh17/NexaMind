import uuid

import pandas as pd


# Temporary in-memory storage.
# We'll replace this with proper storage later.
datasets = {}


def create_dataset(filename: str, sheets: dict):
    dataset_id = str(uuid.uuid4())

    datasets[dataset_id] = {
        "filename": filename,
        "sheets": sheets,
    }

    return dataset_id


def get_dataset(dataset_id: str):
    return datasets.get(dataset_id)