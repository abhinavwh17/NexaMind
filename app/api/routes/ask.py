from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.dataset_service import get_dataset
from app.services.calculation_service import (
    calculate_sum,
    calculate_average,
    calculate_min,
    calculate_max,
    calculate_count,
    calculate_grouped_sum,
)
from app.services.query_planner import QueryPlanner


router = APIRouter(
    prefix="/ask",
    tags=["Ask NexaMind"]
)


class AskRequest(BaseModel):
    dataset_id: str
    question: str


@router.post("")
async def ask_nexamind(request: AskRequest):

    print("\n========================================")
    print("QUESTION:", request.question)
    print("DATASET:", request.dataset_id)
    print("========================================")

    # ---------------------------------------------------------
    # 1. Get uploaded dataset
    # ---------------------------------------------------------

    dataset = get_dataset(request.dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    # ---------------------------------------------------------
    # 2. Get the first sheet for now
    # ---------------------------------------------------------

    sheet_name = next(iter(dataset["sheets"]))

    dataframe = dataset["sheets"][sheet_name]

    columns = [
        str(column)
        for column in dataframe.columns
    ]

    print("\n========== DATASET ==========")
    print("Sheet:", sheet_name)
    print("Columns:", columns)
    print("Rows:", len(dataframe))
    print("=============================")

    # ---------------------------------------------------------
    # 3. Ask Gemini to understand the question
    # ---------------------------------------------------------

    planner = QueryPlanner()

    plan = planner.create_plan(
        request.question,
        columns
    )

    print("\n========== QUERY PLAN ==========")
    print(plan)
    print("================================")

    # ---------------------------------------------------------
    # 4. Extract plan
    # ---------------------------------------------------------

    operation = plan.get("operation")
    column = plan.get("column")
    group_by = plan.get("group_by")

    print("Operation:", operation)
    print("Column:", column)
    print("Group By:", group_by)

    # ---------------------------------------------------------
    # 5. Validate operation
    # ---------------------------------------------------------

    supported_operations = {
        "SUM",
        "AVERAGE",
        "MIN",
        "MAX",
        "COUNT",
        "GROUP_BY",
    }

    if operation not in supported_operations:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported operation: {operation}"
        )

    # ---------------------------------------------------------
    # 6. Validate calculation column
    # ---------------------------------------------------------

    if column not in columns:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid column: {column}"
        )

    # ---------------------------------------------------------
    # 7. GROUP_BY
    # ---------------------------------------------------------

    if operation == "GROUP_BY":

        if not group_by:
            raise HTTPException(
                status_code=400,
                detail="GROUP_BY operation requires a group_by column"
            )

        if group_by not in columns:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid group_by column: {group_by}"
            )

        sort = plan.get("sort", "DESC")
        limit = plan.get("limit")

        print("\n========== GROUP BY ==========")
        print("Group By:", group_by)
        print("Column:", column)
        print("Aggregation:", plan.get("aggregation"))
        print("Sort:", sort)
        print("Limit:", limit)
        print("==============================")

        grouped_result = calculate_grouped_sum(
            dataframe=dataframe,
            group_by=group_by,
            column=column,
            sort=sort,
            limit=limit
        )

        result = grouped_result.to_dict(
            orient="records"
        )

        print("\n========== GROUP RESULT ==========")
        print(result)
        print("===================================")

        return {
            "question": request.question,
            "operation": operation,
            "group_by": group_by,
            "column": column,
            "aggregation": plan.get("aggregation"),
            "result": result,
            "sheet": sheet_name
        }

    # ---------------------------------------------------------
    # 8. Normal calculations
    # ---------------------------------------------------------

    result = None

    if operation == "SUM":

        print("\nExecuting SUM...")

        result = calculate_sum(
            dataframe,
            column
        )

    elif operation == "AVERAGE":

        print("\nExecuting AVERAGE...")

        result = calculate_average(
            dataframe,
            column
        )

    elif operation == "MIN":

        print("\nExecuting MIN...")

        result = calculate_min(
            dataframe,
            column
        )

    elif operation == "MAX":

        print("\nExecuting MAX...")

        result = calculate_max(
            dataframe,
            column
        )

    elif operation == "COUNT":

        print("\nExecuting COUNT...")

        result = calculate_count(
            dataframe,
            column
        )

    # ---------------------------------------------------------
    # 9. Check calculation result
    # ---------------------------------------------------------

    print("\n========== CALCULATION RESULT ==========")
    print("Operation:", operation)
    print("Column:", column)
    print("Result:", result)
    print("========================================")

    if result is None:
        raise HTTPException(
            status_code=500,
            detail="Calculation did not produce a result"
        )

    # ---------------------------------------------------------
    # 10. Return response
    # ---------------------------------------------------------

    return {
        "question": request.question,
        "operation": operation,
        "column": column,
        "result": float(result),
        "sheet": sheet_name
    }