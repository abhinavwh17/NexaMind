from io import BytesIO

import pandas as pd


def analyse_excel(file_content: bytes):
    excel_file = BytesIO(file_content)

    workbook = pd.ExcelFile(excel_file)

    sheets = {}

    for sheet_name in workbook.sheet_names:

        dataframe = pd.read_excel(
            excel_file,
            sheet_name=sheet_name
        )

        sheets[sheet_name] = dataframe

    return sheets


def build_excel_preview(sheets: dict):
    """
    Used by the UI if we want to show a preview.

    IMPORTANT:
    This preview must never be sent to the LLM.
    """

    preview = []

    for sheet_name, dataframe in sheets.items():

        preview.append({
            "name": sheet_name,
            "rows": len(dataframe),
            "columns": len(dataframe.columns),
            "column_names": dataframe.columns.tolist(),
            "preview": dataframe.head(5)
            .fillna("")
            .to_dict(
                orient="records"
            )
        })

    return preview


def build_excel_schema(sheets: dict):
    """
    Builds a privacy-safe representation of one workbook.

    Only structural information is returned.

    NO spreadsheet row values are included.
    """

    schema = {
        "sheets": {}
    }

    for sheet_name, dataframe in sheets.items():

        columns = []

        for column in dataframe.columns:

            series = dataframe[column]

            if pd.api.types.is_numeric_dtype(series):
                column_type = "number"

            elif pd.api.types.is_datetime64_any_dtype(series):
                column_type = "datetime"

            elif pd.api.types.is_bool_dtype(series):
                column_type = "boolean"

            else:
                column_type = "string"

            columns.append({
                "name": str(column),
                "type": column_type
            })

        schema["sheets"][sheet_name] = {
            "columns": columns
        }

    return schema


def build_dataset_schema(dataset: dict):
    """
    Builds the privacy-safe schema catalog for every workbook in an
    analysis workspace.

    This is the only workbook information intended for the LLM:
    - workbook id
    - filename
    - sheet names
    - column names
    - detected column types

    No row or cell values are included.
    """
    schema = {
        "workbooks": []
    }

    for workbook in dataset.get("workbooks", []):
        workbook_schema = build_excel_schema(
            workbook.get("sheets", {})
        )

        schema["workbooks"].append({
            "workbook_id": workbook.get("workbook_id"),
            "filename": workbook.get("filename"),
            "sheets": workbook_schema["sheets"],
        })

    return schema
