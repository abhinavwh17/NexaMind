import json

from app.llm.client import LLMClient


class QueryPlanner:

    def __init__(self):
        self.llm = LLMClient()

    def create_plan(self, question: str, columns: list[str]):

        prompt = f"""
You are a financial data analysis query planner.

Your job is to understand the user's question and convert it into
a structured analysis operation.

You are NOT calculating any values.
You are only determining what calculation the Python application
needs to perform.

Available Excel columns:
{json.dumps(columns)}

User question:
{question}

Supported operations:

SUM
AVERAGE
MIN
MAX
COUNT
GROUP_BY


SEMANTIC RULES

SUM:
Use SUM when the user asks for:
- total
- overall amount
- total amount
- how much in total
- how much did we make
- overall value
- combined value
- total profit
- total revenue
- total sales

Examples:

"What is the total profit?"

{{
    "operation": "SUM",
    "column": "Profit"
}}

"How much profit did we make?"

{{
    "operation": "SUM",
    "column": "Profit"
}}

"What was our overall profit?"

{{
    "operation": "SUM",
    "column": "Profit"
}}


AVERAGE:
Use AVERAGE when the user asks for:
- average
- mean
- typical value
- average amount

Example:

"What is the average profit?"

{{
    "operation": "AVERAGE",
    "column": "Profit"
}}


MAX:
Use MAX when the user asks for:
- highest value
- maximum value
- largest value
- biggest value
- highest profit
- maximum profit

Example:

"What is the highest profit?"

{{
    "operation": "MAX",
    "column": "Profit"
}}


MIN:
Use MIN when the user asks for:
- lowest value
- minimum value
- smallest value
- lowest profit
- minimum profit

Example:

"What is the lowest profit?"

{{
    "operation": "MIN",
    "column": "Profit"
}}


COUNT:
Use COUNT when the user asks:
- how many
- number of
- count
- how many records
- how many entries

Example:

"How many profit records are there?"

{{
    "operation": "COUNT",
    "column": "Profit"
}}


GROUP_BY:
Use GROUP_BY when the user asks to compare a metric
between categories or asks which category has the
highest or lowest total.

Example:

"Which country generated the highest profit?"

{{
    "operation": "GROUP_BY",
    "group_by": "Country",
    "column": "Profit",
    "aggregation": "SUM",
    "sort": "DESC",
    "limit": 1
}}

Example:

"Which country generated the lowest profit?"

{{
    "operation": "GROUP_BY",
    "group_by": "Country",
    "column": "Profit",
    "aggregation": "SUM",
    "sort": "ASC",
    "limit": 1
}}

Example:

"Which product generated the most profit?"

{{
    "operation": "GROUP_BY",
    "group_by": "Product",
    "column": "Profit",
    "aggregation": "SUM",
    "sort": "DESC",
    "limit": 1
}}


IMPORTANT DISTINCTION

Do NOT use GROUP_BY just because the question contains
words such as "highest" or "lowest".

For example:

"What is the highest profit?"

means:

{{
    "operation": "MAX",
    "column": "Profit"
}}

But:

"Which country has the highest profit?"

means:

{{
    "operation": "GROUP_BY",
    "group_by": "Country",
    "column": "Profit",
    "aggregation": "SUM",
    "sort": "DESC",
    "limit": 1
}}


COLUMN MATCHING

Match the user's requested metric to the closest available column.

Examples:

profit -> Profit
revenue -> Sales
sales -> Sales
units -> Units Sold
manufacturing price -> Manufacturing Price
sale price -> Sale Price
discounts -> Discounts
COGS -> COGS

The column must exactly match one of the available columns.

Never invent a column name.

The group_by column must also exactly match one of the available columns.


RULES

1. Understand the meaning of the question, not the exact wording.
2. Do not calculate anything.
3. Do not use financial data.
4. Do not invent columns.
5. Use only the supported operations.
6. Return ONLY valid JSON.
7. Do not return markdown.
8. Do not return ```json.
9. Do not include explanations.
10. Return the smallest JSON object required for the operation.

Return the appropriate JSON object.
"""

        response = self.llm.generate(prompt)

        print("\n========== GEMINI OUTPUT ==========")
        print(response)
        print("===================================\n")

        response = response.strip()

        # Remove markdown code fences if Gemini still returns them
        if response.startswith("```"):
            response = response.replace("```json", "")
            response = response.replace("```", "")
            response = response.strip()

        try:
            plan = json.loads(response)

            print("\n========== PARSED PLAN ==========")
            print(json.dumps(plan, indent=2))
            print("=================================\n")

            return plan

        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid query plan returned by AI: {response}"
            ) from error