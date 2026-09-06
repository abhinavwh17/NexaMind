import pandas as pd
import pytest


@pytest.fixture
def multi_workbook_dataset():
    """
    In-memory dataset matching NexaMind's current multi-workbook structure.

    Transactions = fact table
    Customers    = lookup/reference table
    """
    return {
        "workbooks": [
            {
                "workbook_id": "transactions-wb",
                "filename": "Transactions.xlsx",
                "sheets": {
                    "Transactions": pd.DataFrame(
                        [
                            {
                                "Transaction ID": "T001",
                                "Customer ID": "C001",
                                "Sales": 12000.0,
                                "Profit": 2400.0,
                            },
                            {
                                "Transaction ID": "T002",
                                "Customer ID": "C002",
                                "Sales": 8500.0,
                                "Profit": 1300.0,
                            },
                            {
                                "Transaction ID": "T003",
                                "Customer ID": "C001",
                                "Sales": 9000.0,
                                "Profit": 1800.0,
                            },
                            {
                                "Transaction ID": "T004",
                                "Customer ID": "C999",
                                "Sales": 5000.0,
                                "Profit": 700.0,
                            },
                        ]
                    )
                },
            },
            {
                "workbook_id": "customers-wb",
                "filename": "Customers.xlsx",
                "sheets": {
                    "Customers": pd.DataFrame(
                        [
                            {
                                "Customer ID": "C001",
                                "Customer Name": "Alpha Retail Ltd",
                                "Region": "North",
                                "Segment": "Enterprise",
                            },
                            {
                                "Customer ID": "C002",
                                "Customer Name": "Beacon Foods",
                                "Region": "South",
                                "Segment": "SME",
                            },
                        ]
                    )
                },
            },
        ]
    }


@pytest.fixture
def union_dataset():
    """
    Two compatible workbooks for UNION tests.
    """
    return {
        "workbooks": [
            {
                "workbook_id": "sales-2013-wb",
                "filename": "Financial_Sample_2013.xlsx",
                "sheets": {
                    "Financial Data 2013": pd.DataFrame(
                        [
                            {
                                "Country": "USA",
                                " Sales": 100.0,
                                "Year": 2013,
                            },
                            {
                                "Country": "Canada",
                                " Sales": 200.0,
                                "Year": 2013,
                            },
                        ]
                    )
                },
            },
            {
                "workbook_id": "sales-2014-wb",
                "filename": "Financial_Sample_2014.xlsx",
                "sheets": {
                    "Financial Data 2014": pd.DataFrame(
                        [
                            {
                                "Country": "USA",
                                " Sales": 300.0,
                                "Year": 2014,
                            },
                            {
                                "Country": "Canada",
                                " Sales": 400.0,
                                "Year": 2014,
                            },
                        ]
                    )
                },
            },
        ]
    }
