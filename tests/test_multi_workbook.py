import pandas as pd
import pytest

from app.api.routes.ask import execute_join, execute_union, validate_plan


def test_union_combines_compatible_workbooks(union_dataset):
    calculation = {
        "id": "calc_1",
        "operation": "UNION",
        "sources": [
            {
                "workbook_id": "sales-2013-wb",
                "sheet": "Financial Data 2013",
            },
            {
                "workbook_id": "sales-2014-wb",
                "sheet": "Financial Data 2014",
            },
        ],
    }

    dataframe, result = execute_union(
        dataset=union_dataset,
        calculation=calculation,
    )

    assert len(dataframe) == 4
    assert list(dataframe.columns) == ["Country", " Sales", "Year"]
    assert result["operation"] == "UNION"
    assert result["source_count"] == 2
    assert result["row_count"] == 4


def test_union_rejects_schema_mismatch(union_dataset):
    # Deliberately change the second workbook's schema.
    second_workbook = union_dataset["workbooks"][1]
    second_workbook["sheets"]["Financial Data 2014"] = pd.DataFrame(
        [
            {
                "Country": "USA",
                "Revenue": 300.0,
                "Year": 2014,
            }
        ]
    )

    calculation = {
        "id": "calc_1",
        "operation": "UNION",
        "sources": [
            {
                "workbook_id": "sales-2013-wb",
                "sheet": "Financial Data 2013",
            },
            {
                "workbook_id": "sales-2014-wb",
                "sheet": "Financial Data 2014",
            },
        ],
    }

    with pytest.raises(
        ValueError,
        match="UNION requires identical column names and order",
    ):
        execute_union(
            dataset=union_dataset,
            calculation=calculation,
        )


def test_inner_join_transactions_with_customers(multi_workbook_dataset):
    calculation = {
        "id": "calc_1",
        "operation": "JOIN",
        "left": {
            "workbook_id": "transactions-wb",
            "sheet": "Transactions",
        },
        "right": {
            "workbook_id": "customers-wb",
            "sheet": "Customers",
        },
        "left_on": "Customer ID",
        "right_on": "Customer ID",
        "how": "inner",
    }

    dataframe, result = execute_join(
        dataset=multi_workbook_dataset,
        calculation=calculation,
    )

    # C999 has no customer match, so INNER JOIN removes it.
    assert len(dataframe) == 3
    assert set(dataframe["Region"]) == {"North", "South"}
    assert result["operation"] == "JOIN"
    assert result["how"] == "inner"
    assert result["left_row_count"] == 4
    assert result["right_row_count"] == 2
    assert result["row_count"] == 3


def test_left_join_preserves_unmatched_transactions(multi_workbook_dataset):
    calculation = {
        "id": "calc_1",
        "operation": "JOIN",
        "left": {
            "workbook_id": "transactions-wb",
            "sheet": "Transactions",
        },
        "right": {
            "workbook_id": "customers-wb",
            "sheet": "Customers",
        },
        "left_on": "Customer ID",
        "right_on": "Customer ID",
        "how": "left",
    }

    dataframe, result = execute_join(
        dataset=multi_workbook_dataset,
        calculation=calculation,
    )

    assert len(dataframe) == 4
    unmatched = dataframe[dataframe["Customer ID"] == "C999"]

    assert len(unmatched) == 1
    assert pd.isna(unmatched.iloc[0]["Region"])
    assert result["row_count"] == 4


def test_join_rejects_missing_left_key(multi_workbook_dataset):
    calculation = {
        "id": "calc_1",
        "operation": "JOIN",
        "left": {
            "workbook_id": "transactions-wb",
            "sheet": "Transactions",
        },
        "right": {
            "workbook_id": "customers-wb",
            "sheet": "Customers",
        },
        "left_on": "Missing Customer ID",
        "right_on": "Customer ID",
        "how": "inner",
    }

    with pytest.raises(
        ValueError,
        match="JOIN left column does not exist",
    ):
        execute_join(
            dataset=multi_workbook_dataset,
            calculation=calculation,
        )


def test_join_rejects_duplicate_right_side_keys(multi_workbook_dataset):
    customers = multi_workbook_dataset["workbooks"][1]["sheets"]["Customers"]

    duplicate = pd.DataFrame(
        [
            {
                "Customer ID": "C001",
                "Customer Name": "Duplicate Customer",
                "Region": "West",
                "Segment": "SME",
            }
        ]
    )

    multi_workbook_dataset["workbooks"][1]["sheets"]["Customers"] = pd.concat(
        [customers, duplicate],
        ignore_index=True,
    )

    calculation = {
        "id": "calc_1",
        "operation": "JOIN",
        "left": {
            "workbook_id": "transactions-wb",
            "sheet": "Transactions",
        },
        "right": {
            "workbook_id": "customers-wb",
            "sheet": "Customers",
        },
        "left_on": "Customer ID",
        "right_on": "Customer ID",
        "how": "inner",
    }

    with pytest.raises(
        ValueError,
        match="right-side join key is not unique",
    ):
        execute_join(
            dataset=multi_workbook_dataset,
            calculation=calculation,
        )


def test_plan_rejects_forward_source_result_reference():
    plan = {
        "calculations": [
            {
                "id": "calc_1",
                "operation": "GROUP_BY",
                "source": {
                    "result": "calc_2",
                },
                "group_by": "Region",
                "column": "Sales",
                "aggregation": "SUM",
            },
            {
                "id": "calc_2",
                "operation": "JOIN",
                "left": {
                    "workbook_id": "transactions-wb",
                    "sheet": "Transactions",
                },
                "right": {
                    "workbook_id": "customers-wb",
                    "sheet": "Customers",
                },
                "left_on": "Customer ID",
                "right_on": "Customer ID",
                "how": "inner",
            },
        ],
        "answer_template": "{{calc_1.value}}",
    }

    with pytest.raises(
        ValueError,
        match="before it is available",
    ):
        validate_plan(plan)
