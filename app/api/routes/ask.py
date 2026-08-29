import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.dataset_service import (
    get_dataset,
)

from app.services.excel_service import (
    build_excel_schema,
)

from app.services.calculation_service import (
    execute_calculation,
)

from app.services.query_planner import (
    QueryPlanner,
)


router = APIRouter(
    prefix="/ask",
    tags=["Ask NexaMind"]
)


class AskRequest(BaseModel):

    dataset_id: str
    question: str


# =========================================================
# Formatting
# =========================================================


def format_placeholder_value(
    value
):

    if value is None:
        return "N/A"

    if isinstance(
        value,
        float
    ):

        if value.is_integer():

            return f"{int(value):,}"

        return (
            f"{value:,.2f}"
            .rstrip("0")
            .rstrip(".")
        )

    if isinstance(
        value,
        int
    ):

        return f"{value:,}"

    return str(
        value
    )


# =========================================================
# Template resolver
# =========================================================


def resolve_answer_template(
    template: str,
    calculation_results: list[dict]
):

    results_by_id = {
        result["id"]: result
        for result
        in calculation_results
    }

    placeholder_pattern = re.compile(
        r"\{\{([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\}\}"
    )

    def replace_placeholder(
        match
    ):

        calculation_id = (
            match.group(1)
        )

        field_name = (
            match.group(2)
        )

        result = (
            results_by_id.get(
                calculation_id
            )
        )

        if not result:

            raise ValueError(
                "Unknown calculation placeholder: "
                f"{calculation_id}"
            )

        if field_name not in result:

            raise ValueError(
                "Unknown result field: "
                f"{calculation_id}.{field_name}"
            )

        value = result[
            field_name
        ]

        return format_placeholder_value(
            value
        )

    return placeholder_pattern.sub(
        replace_placeholder,
        template
    )


# =========================================================
# Plan validation
# =========================================================


def validate_plan(
    plan: dict
):

    calculations = (
        plan.get(
            "calculations"
        )
    )

    answer_template = (
        plan.get(
            "answer_template"
        )
    )

    if not isinstance(
        calculations,
        list
    ):

        raise ValueError(
            "Query plan must contain calculations[]"
        )

    if not calculations:

        raise ValueError(
            "Query plan contains no calculations"
        )

    if (
        not isinstance(
            answer_template,
            str
        )
        or
        not answer_template.strip()
    ):

        raise ValueError(
            "Query plan must contain answer_template"
        )

    calculation_ids = set()

    for calculation in calculations:

        if not isinstance(
            calculation,
            dict
        ):

            raise ValueError(
                "Each calculation must be an object"
            )

        calculation_id = (
            calculation.get(
                "id"
            )
        )

        if not calculation_id:

            raise ValueError(
                "Every calculation requires an id"
            )

        if calculation_id in calculation_ids:

            raise ValueError(
                f"Duplicate calculation id: {calculation_id}"
            )

        calculation_ids.add(
            calculation_id
        )


# =========================================================
# API
# =========================================================


@router.post("")
async def ask_nexamind(
    request: AskRequest
):

    print(
        "\n========================================"
    )

    print(
        "QUESTION:",
        request.question
    )

    print(
        "DATASET:",
        request.dataset_id
    )

    print(
        "========================================"
    )

    # -----------------------------------------------------
    # 1. Load dataset
    # -----------------------------------------------------

    dataset = get_dataset(
        request.dataset_id
    )

    if not dataset:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    sheets = dataset.get(
        "sheets"
    )

    if not sheets:

        raise HTTPException(
            status_code=400,
            detail="Dataset contains no Excel sheets"
        )

    # -----------------------------------------------------
    # 2. Build safe schema
    # -----------------------------------------------------

    schema = build_excel_schema(
        sheets
    )

    print(
        "\n========== SAFE SCHEMA =========="
    )

    print(
        schema
    )

    print(
        "================================="
    )

    # -----------------------------------------------------
    # 3. Create AI plan
    # -----------------------------------------------------

    planner = QueryPlanner()

    try:

        plan = planner.create_plan(
            question=request.question,
            schema=schema
        )

    except Exception as error:

        print(
            "Query planner error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to create analysis plan"
        ) from error

    print(
        "\n========== QUERY PLAN =========="
    )

    print(
        plan
    )

    print(
        "================================"
    )

    # -----------------------------------------------------
    # 4. Validate plan
    # -----------------------------------------------------

    try:

        validate_plan(
            plan
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    calculations = (
        plan[
            "calculations"
        ]
    )

    answer_template = (
        plan[
            "answer_template"
        ]
    )

    # -----------------------------------------------------
    # 5. Execute locally
    # -----------------------------------------------------

    calculation_results = []

    for calculation in calculations:

        print(
            "\n========== EXECUTING =========="
        )

        print(
            calculation
        )

        print(
            "================================"
        )

        try:

            result = execute_calculation(
                sheets=sheets,
                calculation=calculation
            )

        except ValueError as error:

            print(
                "Calculation error:",
                error
            )

            raise HTTPException(
                status_code=400,
                detail=str(error)
            ) from error

        calculation_results.append(
            result
        )

        print(
            "\n========== RESULT =========="
        )

        print(
            result
        )

        print(
            "============================"
        )

    # -----------------------------------------------------
    # 6. Resolve scalar placeholders
    # -----------------------------------------------------

    try:

        final_answer = (
            resolve_answer_template(
                template=answer_template,
                calculation_results=calculation_results
            )
        )

    except ValueError as error:

        print(
            "Answer template error:",
            error
        )

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    # -----------------------------------------------------
    # 7. Return
    # -----------------------------------------------------

    response = {
        "question":
            request.question,

        "answer":
            final_answer,

        "calculations":
            calculation_results,
    }

    print(
        "\n========== FINAL RESPONSE =========="
    )

    print(
        response
    )

    print(
        "===================================="
    )

    return response