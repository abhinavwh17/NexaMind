from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.dataset_service import get_dataset
from app.services.calculation_service import calculate_sum


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

    question = request.question.lower()

    # First supported question:
    # "Calculate the total revenue"
    if "total profit" in question:

        for sheet_name, dataframe in dataset["sheets"].items():

            matching_columns = [
                column
                for column in dataframe.columns
                if str(column).lower() == "profit"
            ]

            if matching_columns:

                column = matching_columns[0]

                result = calculate_sum(
                    dataframe,
                    column
                )

                return {
                    "question": request.question,
                    "operation": "SUM",
                    "column": column,
                    "result": result,
                    "sheet": sheet_name
                }

    return {
        "question": request.question,
        "message": "I don't know how to answer this question yet."
    }