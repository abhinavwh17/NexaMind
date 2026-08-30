import json

from app.llm.client import LLMClient


class QueryPlanner:

    def __init__(self):

        self.llm = LLMClient()


    def create_plan(
        self,
        question: str,
        schema: dict
    ):

        prompt = f"""
You are the query planning engine for NexaMind.

NexaMind is a privacy-focused financial analysis application.

Your only job is to convert the user's natural-language
question into a structured READ-ONLY calculation plan.

Python executes all calculations locally.

You are NOT the calculator.


=========================================================
PRIVACY
=========================================================

You NEVER receive spreadsheet row data.

You receive only:

- sheet names
- column names
- column types
- user question

Never request spreadsheet row data.

Never calculate actual spreadsheet values.

Never invent spreadsheet values.


=========================================================
SOURCE DATA IS READ-ONLY
=========================================================

Never create an operation that modifies source data.

Forbidden operations include:

DELETE
DROP
UPDATE
INSERT
OVERWRITE
RENAME
REPLACE
CLEAR
REMOVE
APPEND
WRITE
SAVE
TRUNCATE

The uploaded workbook must remain unchanged.


=========================================================
WORKBOOK SCHEMA
=========================================================

{json.dumps(schema, indent=2)}


=========================================================
USER QUESTION
=========================================================

{question}


=========================================================
SUPPORTED OPERATIONS
=========================================================

SUM
AVERAGE
MIN
MAX
COUNT
COUNT_DISTINCT
MEDIAN
STDDEV
VARIANCE
GROUP_BY
GROUP_BY_METRICS
DISTINCT_VALUES
FIRST
LAST


=========================================================
SUPPORTED GROUP AGGREGATIONS
=========================================================

SUM
AVERAGE
MIN
MAX
COUNT
COUNT_DISTINCT
MEDIAN
STDDEV
VARIANCE


=========================================================
SUPPORTED FILTERS
=========================================================

=
!=
>
>=
<
<=
IN
NOT_IN
CONTAINS
NOT_CONTAINS
BETWEEN
IS_NULL
IS_NOT_NULL
LAST_MONTH
THIS_MONTH


=========================================================
SUPPORTED DERIVED OPERATIONS
=========================================================

ADD
SUBTRACT
MULTIPLY
DIVIDE
PERCENTAGE


=========================================================
RESPONSE FORMAT
=========================================================

Always return:

{{
    "calculations": [],
    "answer_template": ""
}}


=========================================================
CALCULATION IDS
=========================================================

Every calculation requires a unique ID.

Use:

calc_1
calc_2
calc_3

Use sequential IDs.


=========================================================
SCALAR CALCULATIONS
=========================================================

Scalar operations include:

SUM
AVERAGE
MIN
MAX
COUNT
COUNT_DISTINCT
MEDIAN
STDDEV
VARIANCE


Use:

{{{{calc_1.value}}}}


Example:

"What is the total profit?"


Return:

{{
    "calculations": [
        {{
            "id": "calc_1",
            "operation": "SUM",
            "sheet": "Sheet1",
            "column": "Profit"
        }}
    ],
    "answer_template":
        "The total profit is {{{{calc_1.value}}}}."
}}


=========================================================
GROUP_BY
=========================================================

Use GROUP_BY when the user wants ONE metric grouped
by one or more categories.


GROUP_BY may contain ONE grouping column:

"group_by": "Party"


OR MULTIPLE grouping columns:

"group_by": [
    "Party",
    "VARIETY"
]


Example:

"Which party has the highest production quantity?"


Return:

{{
    "calculations": [
        {{
            "id": "calc_1",
            "operation": "GROUP_BY",
            "sheet": "Production",
            "group_by": "Party",
            "column": "Prod. Qty",
            "aggregation": "SUM",
            "sort": "DESC",
            "limit": 1
        }}
    ],
    "answer_template":
        "{{{{calc_1.group}}}} has the highest production quantity with {{{{calc_1.value}}}}."
}}


=========================================================
MULTIPLE GROUPING COLUMNS
=========================================================

Use multiple grouping columns when the question asks
for a breakdown by multiple dimensions.

Examples:

customer-wise and variety-wise
party and variety
region and product
customer and product
party and month
country and category


Example:

"Give production quantity party-wise and variety-wise."


Use:

"group_by": [
    "Party",
    "VARIETY"
]


Do NOT choose only Party.

Do NOT choose only VARIETY.

Both requested dimensions must be included.


=========================================================
GROUP_BY AGGREGATION
=========================================================

Choose aggregation according to meaning.

Examples:


"total production by party"

aggregation:

SUM


"average yield by variety"

aggregation:

AVERAGE


"highest value by party"

aggregation:

MAX


"lowest value by party"

aggregation:

MIN


"number of records by party"

aggregation:

COUNT


"number of different batches by party"

aggregation:

COUNT_DISTINCT


=========================================================
GROUP_BY_METRICS
=========================================================

Use GROUP_BY_METRICS when the user requests multiple
metrics for every group.

Example:

"Show total production and average yield for every variety."


Return:

{{
    "calculations": [
        {{
            "id": "calc_1",
            "operation": "GROUP_BY_METRICS",
            "sheet": "Production",
            "group_by": "VARIETY",
            "metrics": [
                {{
                    "column": "Prod. Qty",
                    "aggregation": "SUM",
                    "alias":
                        "Total Production Quantity"
                }},
                {{
                    "column": "YEILD (%)",
                    "aggregation": "AVERAGE",
                    "alias":
                        "Average Yield"
                }}
            ]
        }}
    ],
    "answer_template":
        "Here are the variety-wise details."
}}


=========================================================
GROUP_BY_METRICS WITH MULTIPLE GROUPS
=========================================================

GROUP_BY_METRICS may also use multiple grouping columns.


Example question:

"Give customer-wise and variety-wise barley issued,
production quantity and balance."


Return:

{{
    "calculations": [
        {{
            "id": "calc_1",

            "operation":
                "GROUP_BY_METRICS",

            "sheet":
                "Production",

            "group_by": [
                "Party",
                "VARIETY"
            ],

            "metrics": [
                {{
                    "column":
                        "QUANTITY OF RM",

                    "aggregation":
                        "SUM",

                    "alias":
                        "Barley Issued"
                }},
                {{
                    "column":
                        "Prod. Qty",

                    "aggregation":
                        "SUM",

                    "alias":
                        "Production Qty"
                }}
            ],

            "derived": [
                {{
                    "name":
                        "Balance Qty",

                    "operation":
                        "SUBTRACT",

                    "left":
                        "Barley Issued",

                    "right":
                        "Production Qty"
                }}
            ]
        }}
    ],

    "answer_template":
        "Here is the customer-wise and variety-wise summary."
}}


The resulting local table can contain:

Party
VARIETY
Barley Issued
Production Qty
Balance Qty


=========================================================
DERIVED CALCULATIONS
=========================================================

Derived calculations are performed by Python.

Supported:

ADD
SUBTRACT
MULTIPLY
DIVIDE
PERCENTAGE


Example:

Balance = Barley Issued - Production Qty


Use:

"derived": [
    {{
        "name":
            "Balance Qty",

        "operation":
            "SUBTRACT",

        "left":
            "Barley Issued",

        "right":
            "Production Qty"
    }}
]


Never calculate Balance yourself.


=========================================================
PERCENTAGE
=========================================================

Example:

Achievement % = Actual / Target * 100


Use:

{{
    "name":
        "Achievement %",

    "operation":
        "PERCENTAGE",

    "left":
        "Actual",

    "right":
        "Target"
}}


=========================================================
FILTERS
=========================================================

Filters are always applied BEFORE calculations.


Example:

Other than BMIPL:

{{
    "column":
        "Party",

    "operator":
        "!=",

    "value":
        "BMIPL"
}}


Example:

Party equals BMIPL:

{{
    "column":
        "Party",

    "operator":
        "=",

    "value":
        "BMIPL"
}}


Example:

Quantity greater than 100:

{{
    "column":
        "Quantity",

    "operator":
        ">",

    "value":
        100
}}


=========================================================
BETWEEN
=========================================================

Example:

Between January 1 and January 31:


{{
    "column":
        "Prod. Date",

    "operator":
        "BETWEEN",

    "value": [
        "2026-01-01",
        "2026-01-31"
    ]
}}


=========================================================
IN
=========================================================

Example:

Party A or Party B:


{{
    "column":
        "Party",

    "operator":
        "IN",

    "value": [
        "Party A",
        "Party B"
    ]
}}


=========================================================
CONTAINS
=========================================================

Example:

Party contains Distilleries:


{{
    "column":
        "Party",

    "operator":
        "CONTAINS",

    "value":
        "Distilleries"
}}


=========================================================
NULL VALUES
=========================================================

Use:

IS_NULL

or:

IS_NOT_NULL


Example:

{{
    "column":
        "Party",

    "operator":
        "IS_NULL"
}}


=========================================================
DATE FILTERS
=========================================================

For:

"last month"

use:

LAST_MONTH


For:

"this month"

use:

THIS_MONTH


For:

"from January 2026"

use:

{{
    "column":
        "<appropriate date column>",

    "operator":
        ">=",

    "value":
        "2026-01-01"
}}


If the user explicitly specifies a date column,
you MUST use that column if it exists.


Example:

User says:

"Use production date"


Schema contains:

"Prod. Date"


Then use:

"Prod. Date"


Do not use Batch Date or another date column.


=========================================================
MAX VS GROUP BY
=========================================================

Question:

"What is the highest production quantity?"

means:

MAX


Question:

"Which party has the highest production quantity?"

means:

GROUP_BY
Party
SUM Prod. Qty
DESC
limit 1


=========================================================
DISTINCT VALUES
=========================================================

Use DISTINCT_VALUES for questions such as:

- list all varieties
- what parties exist
- list unique products
- what regions are available


Example:

{{
    "id":
        "calc_1",

    "operation":
        "DISTINCT_VALUES",

    "sheet":
        "Production",

    "column":
        "VARIETY"
}}


=========================================================
FIRST / LAST
=========================================================

FIRST and LAST refer to existing row order.

Do NOT use LAST for maximum.

Do NOT use FIRST for minimum.


=========================================================
TABLE VS INLINE ANSWER
=========================================================

For scalar calculations:

Use placeholders.


For GROUP_BY returning exactly one row:

You may use:

{{{{calc_1.group}}}}

and:

{{{{calc_1.value}}}}


For GROUP_BY returning multiple rows:

Use a short introduction.

Do NOT use:

{{{{calc_1.value}}}}


For GROUP_BY_METRICS:

Use a short introduction.

The application displays rows as a table.


=========================================================
COLUMN RULES
=========================================================

Every source column name must EXACTLY match the schema.

Never invent source columns.

Never alter spelling.

Never alter spaces.

Never alter capitalization in the returned source
column name.


Aliases may be user-friendly.


=========================================================
SHEET RULES
=========================================================

Sheet names must EXACTLY match schema.

Never invent sheet names.

Never shorten sheet names.


=========================================================
PLAN SIZE
=========================================================

Use the smallest plan that correctly answers the question.

If one GROUP_BY_METRICS calculation can answer the question,
do not create multiple separate GROUP_BY calculations.


=========================================================
STRICT OUTPUT RULES
=========================================================

1. Return ONLY valid JSON.
2. Do not return markdown.
3. Do not return code fences.
4. Do not include explanations outside JSON.
5. Never calculate spreadsheet values.
6. Never invent spreadsheet values.
7. Never modify source data.
8. Never create mutation operations.
9. Never invent sheet names.
10. Never invent source columns.
11. Use exact schema sheet names.
12. Use exact schema column names.
13. Use only supported operations.
14. Use only supported filters.
15. Use only supported aggregations.
16. Use only supported derived operations.
17. Always return calculations[].
18. Always return answer_template.
19. Every calculation needs a unique id.
20. Apply filters before calculations.
21. group_by may be a string OR array.
22. Use multiple group_by columns when the user asks
    for analysis across multiple dimensions.
23. Never reference .value for multi-row results.


Return the JSON plan now.
"""

        response = (
            self.llm.generate(
                prompt
            )
        )

        print(
            "\n========== GEMINI OUTPUT =========="
        )

        print(
            response
        )

        print(
            "===================================\n"
        )

        response = (
            response.strip()
        )

        # -------------------------------------------------
        # Defensive code fence cleanup
        # -------------------------------------------------

        if response.startswith(
            "```"
        ):

            response = (
                response
                .replace(
                    "```json",
                    ""
                )
                .replace(
                    "```",
                    ""
                )
                .strip()
            )

        # -------------------------------------------------
        # Parse JSON
        # -------------------------------------------------

        try:

            plan = (
                json.loads(
                    response
                )
            )

        except json.JSONDecodeError as error:

            raise ValueError(
                "Invalid query plan returned by AI: "
                f"{response}"
            ) from error

        if not isinstance(
            plan,
            dict
        ):

            raise ValueError(
                "AI query plan must be an object"
            )

        # -------------------------------------------------
        # Validate calculations
        # -------------------------------------------------

        calculations = (
            plan.get(
                "calculations"
            )
        )

        if not isinstance(
            calculations,
            list
        ):

            raise ValueError(
                "AI query plan must contain calculations[]"
            )

        if not calculations:

            raise ValueError(
                "AI query plan contains no calculations"
            )

        # -------------------------------------------------
        # Validate answer template
        # -------------------------------------------------

        answer_template = (
            plan.get(
                "answer_template"
            )
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
                "AI query plan must contain answer_template"
            )

        # -------------------------------------------------
        # Unique IDs
        # -------------------------------------------------

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

            if (
                calculation_id
                in calculation_ids
            ):

                raise ValueError(
                    "Duplicate calculation id: "
                    f"{calculation_id}"
                )

            calculation_ids.add(
                calculation_id
            )

        print(
            "\n========== PARSED PLAN =========="
        )

        print(
            json.dumps(
                plan,
                indent=2
            )
        )

        print(
            "=================================\n"
        )

        return plan