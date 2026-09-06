import pytest

import app.api.routes.ask as ask_module
from app.api.routes.ask import AskRequest, ask_nexamind
from app.services import dataset_service


@pytest.mark.asyncio
async def test_join_then_group_by_source_result_pipeline(
    multi_workbook_dataset,
    monkeypatch,
):
    """
    End-to-end backend pipeline without making a real Gemini request:

        JOIN
          -> local intermediate DataFrame
          -> source.result
          -> GROUP_BY Region / SUM Sales
          -> answer template

    QueryPlanner itself is replaced so its constructor never creates
    a real Gemini client.
    """
    dataset_id = "test-join-dataset"

    dataset_service.datasets[dataset_id] = (
        multi_workbook_dataset
    )

    plan = {
        "calculations": [
            {
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
            },
            {
                "id": "calc_2",
                "operation": "GROUP_BY",
                "source": {
                    "result": "calc_1",
                },
                "group_by": "Region",
                "column": "Sales",
                "aggregation": "SUM",
                "sort": "DESC",
                "limit": 1,
            },
        ],
        "answer_template": (
            "{{calc_2.group}} generated the highest sales "
            "with {{calc_2.value}}."
        ),
    }

    class FakeQueryPlanner:
        def create_plan(self, question, schema):
            return plan

    monkeypatch.setattr(
        ask_module,
        "QueryPlanner",
        FakeQueryPlanner,
    )

    try:
        response = await ask_nexamind(
            AskRequest(
                dataset_id=dataset_id,
                question="Which customer region generated the highest sales?",
            )
        )
    finally:
        dataset_service.datasets.pop(
            dataset_id,
            None,
        )

    assert response["answer"] == (
        "North generated the highest sales with 21,000."
    )

    assert len(response["calculations"]) == 2

    join_result = response["calculations"][0]
    grouped_result = response["calculations"][1]

    assert join_result["operation"] == "JOIN"
    assert join_result["row_count"] == 3

    assert grouped_result["operation"] == "GROUP_BY"
    assert grouped_result["group"] == "North"
    assert grouped_result["value"] == 21000.0
    assert grouped_result["source"] == {
        "result": "calc_1"
    }
