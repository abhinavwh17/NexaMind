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
    preview = []

    for sheet_name, dataframe in sheets.items():
        preview.append({
            "name": sheet_name,
            "rows": len(dataframe),
            "columns": len(dataframe.columns),
            "column_names": dataframe.columns.tolist(),
            "preview": dataframe.head(5).fillna("").to_dict(
                orient="records"
            )
        })

    return preview