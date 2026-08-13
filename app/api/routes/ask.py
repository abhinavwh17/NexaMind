from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.dataset_service import get_dataset
from app.services.calculation_service import (
    calculate_sum,
    calculate_average,
    calculate_min,
    calculate_max,
    calculate_count,
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

    dataset = get_dataset(request.dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    # Get the first sheet for now
    sheet_name = next(iter(dataset["sheets"]))

    dataframe = dataset["sheets"][sheet_name]

    columns = [
        str(column)
        for column in dataframe.columns
    ]

    # Ask Gemini to create a query plan
    planner = QueryPlanner()

    plan = planner.create_plan(
        request.question,
        columns
    )

    operation = plan.get("operation")
    column = plan.get("column")

    # Validate operation
    supported_operations = {
        "SUM",
        "AVERAGE",
        "MIN",
        "MAX",
        "COUNT"
    }

    if operation not in supported_operations:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported operation: {operation}"
        )

    # Validate column
    if column not in columns:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid column: {column}"
        )

    # Execute calculation in Python
    if operation == "SUM":
        result = calculate_sum(dataframe, column)

    elif operation == "AVERAGE":
        result = calculate_average(dataframe, column)

    elif operation == "MIN":
        result = calculate_min(dataframe, column)

    elif operation == "MAX":
        result = calculate_max(dataframe, column)

    elif operation == "COUNT":
        result = calculate_count(dataframe, column)

    return {
        "question": request.question,
        "operation": operation,
        "column": column,
        "result": float(result),
        "sheet": sheet_name
    }