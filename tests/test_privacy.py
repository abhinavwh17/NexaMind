import json

from app.services.excel_service import build_dataset_schema


def test_dataset_schema_contains_structure_but_not_row_values(
    multi_workbook_dataset,
):
    """
    This protects NexaMind's core privacy boundary.

    The object intended for Gemini may contain:
      - workbook ids / filenames
      - sheet names
      - column names
      - column types

    It must not contain workbook row/cell values.
    """
    schema = build_dataset_schema(
        multi_workbook_dataset
    )

    serialized = json.dumps(
        schema,
        default=str,
    )

    # Structural metadata SHOULD be present.
    assert "Transactions.xlsx" in serialized
    assert "Customers.xlsx" in serialized
    assert "Transactions" in serialized
    assert "Customers" in serialized
    assert "Customer ID" in serialized
    assert "Sales" in serialized
    assert "Region" in serialized

    # Raw workbook values MUST NOT be present.
    assert "T001" not in serialized
    assert "C001" not in serialized
    assert "Alpha Retail Ltd" not in serialized
    assert "Beacon Foods" not in serialized
    assert "12000" not in serialized
    assert "8500" not in serialized


def test_schema_does_not_expose_preview_or_rows(multi_workbook_dataset):
    schema = build_dataset_schema(
        multi_workbook_dataset
    )

    serialized = json.dumps(
        schema,
        default=str,
    ).lower()

    assert '"preview"' not in serialized
    assert '"rows"' not in serialized
    assert '"data"' not in serialized
