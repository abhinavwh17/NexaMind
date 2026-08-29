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
You are the query planning engine for NexaMind,
a privacy-focused financial analysis application.

Your job is to convert the user's natural-language question
into a structured calculation plan that the Python backend
can execute locally.

You are NOT a calculator.

You NEVER receive actual spreadsheet row data.

You only receive:

- sheet names
- column names
- column types

The actual spreadsheet data remains private inside Python.

Never calculate the final answer yourself.
Never invent spreadsheet values.


=========================================================
AVAILABLE WORKBOOK SCHEMA
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
GROUP_BY
GROUP_BY_METRICS


=========================================================
SUPPORTED FILTER OPERATORS
=========================================================

=
!=
>
>=
<
<=
LAST_MONTH
THIS_MONTH


=========================================================
STANDARD RESPONSE FORMAT
=========================================================

Always return:

{{
    "calculations": [...],
    "answer_template": "..."
}}


=========================================================
SCALAR PLACEHOLDERS
=========================================================

For SUM, AVERAGE, MIN, MAX and COUNT:

{{{{calc_1.value}}}}


For GROUP_BY when limit = 1:

{{{{calc_1.group}}}}
{{{{calc_1.value}}}}


IMPORTANT:

Do NOT use:

{{{{calc_1.value}}}}

for GROUP_BY returning multiple rows.

Do NOT use:

{{{{calc_1.value}}}}

for GROUP_BY_METRICS.

Those operations return rows instead.


=========================================================
SUM
=========================================================

Use SUM for questions like:

- total
- total profit
- total sales
- total quantity
- combined amount
- overall amount


Example:

"What is total profit?"

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
AVERAGE
=========================================================

Use AVERAGE for:

- average
- mean
- typical value


=========================================================
MAX
=========================================================

Use MAX when asking for the largest individual value.

Example:

"What is the highest production quantity?"

means:

MAX Prod. Qty


=========================================================
MIN
=========================================================

Use MIN when asking for the smallest individual value.


=========================================================
COUNT
=========================================================

Use COUNT for:

- how many
- number of records
- count


=========================================================
GROUP_BY
=========================================================

Use GROUP_BY when comparing ONE metric across categories.

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
        "{{{{calc_1.group}}}} had the highest production quantity with {{{{calc_1.value}}}}."
}}


IMPORTANT DIFFERENCE:

"What is the highest production quantity?"

means:

MAX


"Which party has the highest production quantity?"

means:

GROUP_BY Party
SUM Prod. Qty
DESC
limit 1


=========================================================
GROUP_BY_METRICS
=========================================================

Use GROUP_BY_METRICS when the user requests:

- every party
- each party
- party-wise data
- every customer
- customer-wise data
- every product
- product-wise data
- multiple metrics for each group
- balance/difference/remaining amount for each group
- a table-like result


GROUP_BY_METRICS contains:

group_by
metrics[]
derived[]
filters[]


Example:

"For every party show barley issued,
production and balance from January 2026."


Return:

{{
    "calculations": [
        {{
            "id": "calc_1",
            "operation": "GROUP_BY_METRICS",
            "sheet": "Production",
            "group_by": "Party",

            "metrics": [
                {{
                    "column": "QUANTITY OF RM",
                    "aggregation": "SUM",
                    "alias": "Barley Issued"
                }},
                {{
                    "column": "Prod. Qty",
                    "aggregation": "SUM",
                    "alias": "Production"
                }}
            ],

            "derived": [
                {{
                    "name": "Balance",
                    "operation": "SUBTRACT",
                    "left": "Barley Issued",
                    "right": "Production"
                }}
            ],

            "filters": [
                {{
                    "column": "Prod. Date",
                    "operator": ">=",
                    "value": "2026-01-01"
                }}
            ]
        }}
    ],

    "answer_template":
        "Here is the party-wise barley issued, production and balance from January 2026 to date."
}}


IMPORTANT:

If the user asks for multiple metrics for every group,
DO NOT create separate GROUP_BY calculations.

Use ONE GROUP_BY_METRICS operation.


=========================================================
DERIVED CALCULATIONS
=========================================================

Currently supported derived operation:

SUBTRACT


Example:

Balance = Barley Issued - Production


Represent it as:

{{
    "name": "Balance",
    "operation": "SUBTRACT",
    "left": "Barley Issued",
    "right": "Production"
}}


Do NOT calculate the result yourself.


=========================================================
FILTERS
=========================================================

Filters are applied BEFORE calculations.


Example:

"other than BMIPL"

{{
    "column": "Party",
    "operator": "!=",
    "value": "BMIPL"
}}


Example:

"last month"

{{
    "column": "Prod. Date",
    "operator": "LAST_MONTH"
}}


Example:

"this month"

{{
    "column": "Prod. Date",
    "operator": "THIS_MONTH"
}}


Example:

"from January 2026"

{{
    "column": "Prod. Date",
    "operator": ">=",
    "value": "2026-01-01"
}}


Multiple filters use AND logic.


=========================================================
DATE COLUMN RULES
=========================================================

If the user explicitly specifies which date column to use,
you MUST use that exact date column if it exists.

Example:

User says:

"use Production Date"

and schema contains:

"Prod. Date"

Then use:

"Prod. Date"


Do not replace it with:

"Batch Date"
"Date"
"Date.1"


=========================================================
COLUMN RULES
=========================================================

Column names must EXACTLY match the schema.

Never invent column names.

If the user explicitly names a column and it exists,
prefer that exact column.


=========================================================
SHEET RULES
=========================================================

Sheet names must EXACTLY match the schema.

Never:

- shorten sheet names
- rename sheet names
- invent sheet names


=========================================================
ANSWER TEMPLATE RULES
=========================================================

For scalar calculations:

use placeholders.


For GROUP_BY limit 1:

use:

{{{{calc_1.group}}}}
{{{{calc_1.value}}}}


For GROUP_BY_METRICS:

return only a natural introduction.

Example:

"Here is the requested party-wise breakdown."


Do NOT use:

{{{{calc_1.value}}}}

for GROUP_BY_METRICS because it returns rows.


=========================================================
STRICT OUTPUT RULES
=========================================================

1. Return ONLY valid JSON.
2. No markdown.
3. No ```json.
4. No code fences.
5. No explanations outside JSON.
6. Never calculate spreadsheet values.
7. Never invent sheet names.
8. Never invent columns.
9. Use only supported operations.
10. Use only supported filters.
11. Every calculation requires a unique id.
12. Use calc_1, calc_2, calc_3 sequentially.
13. Always return calculations as an array.
14. Always return answer_template.
15. Include every filter required by the question.
16. Prefer GROUP_BY_METRICS when the user wants multiple
    metrics for every group.
17. Never reference .value for a multi-row table result.


Return the JSON plan now.
"""

        response = self.llm.generate(
            prompt
        )

        print(
            "\n========== GEMINI OUTPUT =========="
        )
        print(response)
        print(
            "===================================\n"
        )

        response = response.strip()

        if response.startswith("```"):

            response = response.replace(
                "```json",
                ""
            )

            response = response.replace(
                "```",
                ""
            )

            response = response.strip()

        try:

            plan = json.loads(
                response
            )

        except json.JSONDecodeError as error:

            raise ValueError(
                f"Invalid query plan returned by AI: {response}"
            ) from error

        if not isinstance(
            plan,
            dict
        ):
            raise ValueError(
                "AI query plan must be a JSON object"
            )

        calculations = plan.get(
            "calculations"
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

        answer_template = plan.get(
            "answer_template"
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
                calculation.get("id")
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