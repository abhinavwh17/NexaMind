import re

import pandas as pd

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.dataset_service import (
    get_dataset,
    get_workbook,
    get_workbooks,
)

from app.services.excel_service import (
    build_dataset_schema,
)

from app.services.calculation_service import (
    SUPPORTED_RESULT_OPERATIONS,
    execute_calculation,
    execute_result_calculation,
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
# Cross-workbook dataset operations
# =========================================================

SUPPORTED_DATASET_OPERATIONS = {
    "UNION",
}


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
    available_result_ids = set()
    available_dataset_result_ids = set()

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

        operation = str(
            calculation.get(
                "operation",
                ""
            )
        ).upper()

        if not operation:

            raise ValueError(
                f"Calculation '{calculation_id}' requires an operation"
            )

        # =================================================
        # Result-based scalar calculations
        # =================================================

        if (
            operation
            in SUPPORTED_RESULT_OPERATIONS
        ):

            if operation == "COMPARE":

                for side in [
                    "left",
                    "right",
                ]:

                    reference = (
                        calculation.get(
                            side
                        )
                    )

                    if not isinstance(
                        reference,
                        dict
                    ):

                        raise ValueError(
                            f"COMPARE '{calculation_id}' "
                            f"requires a {side} result reference"
                        )

                    reference_id = (
                        reference.get(
                            "calculation_id"
                        )
                    )

                    field = (
                        reference.get(
                            "field",
                            "value"
                        )
                    )

                    if not reference_id:

                        raise ValueError(
                            f"COMPARE '{calculation_id}' "
                            f"{side} reference requires calculation_id"
                        )

                    if (
                        reference_id
                        not in available_result_ids
                    ):

                        raise ValueError(
                            f"COMPARE '{calculation_id}' references "
                            f"'{reference_id}' before it is available"
                        )

                    if (
                        not isinstance(
                            field,
                            str
                        )
                        or
                        not field.strip()
                    ):

                        raise ValueError(
                            f"COMPARE '{calculation_id}' "
                            f"{side} reference requires a valid field"
                        )

        # =================================================
        # Dataset-producing calculations
        # =================================================

        elif (
            operation
            in SUPPORTED_DATASET_OPERATIONS
        ):

            if operation == "UNION":

                sources = (
                    calculation.get(
                        "sources"
                    )
                )

                if (
                    not isinstance(
                        sources,
                        list
                    )
                    or
                    len(sources) < 2
                ):

                    raise ValueError(
                        f"UNION '{calculation_id}' requires "
                        "at least two sources"
                    )

                for source in sources:

                    if not isinstance(
                        source,
                        dict
                    ):

                        raise ValueError(
                            f"UNION '{calculation_id}' "
                            "sources must be objects"
                        )

                    if not source.get(
                        "workbook_id"
                    ):

                        raise ValueError(
                            f"UNION '{calculation_id}' source "
                            "requires workbook_id"
                        )

                    if not source.get(
                        "sheet"
                    ):

                        raise ValueError(
                            f"UNION '{calculation_id}' source "
                            "requires sheet"
                        )

        # =================================================
        # Normal workbook or intermediate-dataset operation
        # =================================================

        else:

            source = calculation.get(
                "source"
            )

            if source is not None:

                if not isinstance(
                    source,
                    dict
                ):

                    raise ValueError(
                        f"Calculation '{calculation_id}' "
                        "source must be an object"
                    )

                result_id = source.get(
                    "result"
                )

                if not result_id:

                    raise ValueError(
                        f"Calculation '{calculation_id}' "
                        "source requires result"
                    )

                if (
                    result_id
                    not in available_dataset_result_ids
                ):

                    raise ValueError(
                        f"Calculation '{calculation_id}' references "
                        f"dataset result '{result_id}' before it is available"
                    )

        calculation_ids.add(
            calculation_id
        )

        available_result_ids.add(
            calculation_id
        )

        if (
            operation
            in SUPPORTED_DATASET_OPERATIONS
        ):

            available_dataset_result_ids.add(
                calculation_id
            )


# =========================================================
# UNION execution
# =========================================================


def execute_union(
    dataset: dict,
    calculation: dict
):
    """
    Create a temporary local DataFrame by vertically combining
    compatible workbook sheets.

    No source workbook is mutated.
    No row data is sent to the LLM.
    """

    sources = calculation.get(
        "sources",
        []
    )

    dataframes = []
    expected_columns = None

    for source in sources:

        workbook_id = source.get(
            "workbook_id"
        )

        sheet_name = source.get(
            "sheet"
        )

        workbook = get_workbook(
            dataset,
            workbook_id
        )

        if not workbook:

            raise ValueError(
                "Unknown workbook_id in UNION: "
                f"{workbook_id}"
            )

        sheets = workbook.get(
            "sheets",
            {}
        )

        if sheet_name not in sheets:

            raise ValueError(
                f"Sheet '{sheet_name}' does not exist in "
                f"workbook '{workbook['filename']}'"
            )

        dataframe = (
            sheets[
                sheet_name
            ]
            .copy()
        )

        columns = [
            str(column)
            for column
            in dataframe.columns
        ]

        if expected_columns is None:

            expected_columns = columns

        elif columns != expected_columns:

            raise ValueError(
                "UNION requires identical column names and order "
                "across all source sheets"
            )

        dataframes.append(
            dataframe
        )

    if not dataframes:

        raise ValueError(
            "UNION has no source data"
        )

    union_dataframe = pd.concat(
        dataframes,
        ignore_index=True,
        copy=True
    )

    result = {
        "id":
            calculation[
                "id"
            ],

        "operation":
            "UNION",

        "source_count":
            len(
                sources
            ),

        "row_count":
            len(
                union_dataframe
            ),

        "columns":
            [
                str(column)
                for column
                in union_dataframe.columns
            ],
    }

    return (
        union_dataframe,
        result
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

    workbooks = get_workbooks(
        dataset
    )

    if not workbooks:

        raise HTTPException(
            status_code=400,
            detail="Dataset contains no Excel workbooks"
        )

    # -----------------------------------------------------
    # 2. Build privacy-safe multi-workbook schema catalog
    # -----------------------------------------------------

    schema = build_dataset_schema(
        dataset
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

    # Temporary DataFrames produced by calculations such as UNION.
    # These stay only in local memory and are never returned to Gemini.
    intermediate_datasets = {}

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

        operation = str(
            calculation.get(
                "operation",
                ""
            )
        ).upper()

        # =================================================
        # A. Result-based scalar calculations
        # =================================================

        if (
            operation
            in SUPPORTED_RESULT_OPERATIONS
        ):

            try:

                result = execute_result_calculation(
                    calculation=calculation,
                    calculation_results=calculation_results
                )

            except ValueError as error:

                print(
                    "Result calculation error:",
                    error
                )

                raise HTTPException(
                    status_code=400,
                    detail=str(error)
                ) from error

        # =================================================
        # B. Dataset-producing calculations
        # =================================================

        elif (
            operation
            in SUPPORTED_DATASET_OPERATIONS
        ):

            try:

                (
                    intermediate_dataframe,
                    result
                ) = execute_union(
                    dataset=dataset,
                    calculation=calculation
                )

                intermediate_datasets[
                    calculation[
                        "id"
                    ]
                ] = intermediate_dataframe

            except ValueError as error:

                print(
                    "Dataset calculation error:",
                    error
                )

                raise HTTPException(
                    status_code=400,
                    detail=str(error)
                ) from error

        # =================================================
        # C. Analysis over an intermediate dataset
        # =================================================

        elif calculation.get(
            "source"
        ):

            source = calculation[
                "source"
            ]

            source_result_id = source.get(
                "result"
            )

            dataframe = intermediate_datasets.get(
                source_result_id
            )

            if dataframe is None:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Unknown intermediate dataset result: "
                        f"{source_result_id}"
                    )
                )

            # Reuse the existing trusted calculation engine by
            # exposing the temporary DataFrame as an internal sheet.
            internal_sheet_name = "__nexamind_result__"

            execution_calculation = dict(
                calculation
            )

            execution_calculation[
                "sheet"
            ] = internal_sheet_name

            execution_calculation.pop(
                "source",
                None
            )

            try:

                result = execute_calculation(
                    sheets={
                        internal_sheet_name:
                            dataframe
                    },
                    calculation=execution_calculation
                )

                result[
                    "source"
                ] = {
                    "result":
                        source_result_id
                }

                # Internal sheet name should not leak into the UI.
                result.pop(
                    "sheet",
                    None
                )

            except ValueError as error:

                print(
                    "Intermediate calculation error:",
                    error
                )

                raise HTTPException(
                    status_code=400,
                    detail=str(error)
                ) from error

        # =================================================
        # D. Direct workbook calculations
        # =================================================

        else:

            workbook_id = calculation.get(
                "workbook_id"
            )

            if (
                not workbook_id
                and
                len(workbooks) == 1
            ):

                workbook_id = (
                    workbooks[0][
                        "workbook_id"
                    ]
                )

                calculation[
                    "workbook_id"
                ] = workbook_id

            if not workbook_id:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Calculation must specify workbook_id "
                        "when multiple workbooks are uploaded"
                    )
                )

            workbook = get_workbook(
                dataset,
                workbook_id
            )

            if not workbook:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Unknown workbook_id: "
                        f"{workbook_id}"
                    )
                )

            sheets = workbook.get(
                "sheets",
                {}
            )

            sheet_name = calculation.get(
                "sheet"
            )

            if sheet_name not in sheets:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Sheet '{sheet_name}' does not exist in "
                        f"workbook '{workbook['filename']}'"
                    )
                )

            try:

                result = execute_calculation(
                    sheets=sheets,
                    calculation=calculation
                )

                result[
                    "workbook_id"
                ] = workbook_id

                result[
                    "workbook"
                ] = workbook[
                    "filename"
                ]

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