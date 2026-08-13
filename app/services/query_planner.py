import json

from app.llm.client import LLMClient


class QueryPlanner:

    def __init__(self):
        self.llm = LLMClient()

    def create_plan(self, question: str, columns: list[str]):

        prompt = f"""
You are a financial data analysis query planner.

Available Excel columns:
{json.dumps(columns)}

User question:
{question}

Determine the calculation required.

Supported operations:

SUM
AVERAGE
MIN
MAX
COUNT

Examples:

"Calculate the total profit"
-> {{"operation": "SUM", "column": "Profit"}}

"What is the highest profit?"
-> {{"operation": "MAX", "column": "Profit"}}

"What is the lowest profit?"
-> {{"operation": "MIN", "column": "Profit"}}

"What is the average profit?"
-> {{"operation": "AVERAGE", "column": "Profit"}}

"How many profit records are there?"
-> {{"operation": "COUNT", "column": "Profit"}}

Rules:

- Match the requested metric to the closest available column.
- The column must exactly match one of the available columns.
- Do not invent column names.
- Return ONLY valid JSON.
- Do not use markdown.
- Do not include ```json.
- Do not include explanations.

Return this format:

{{
    "operation": "SUM",
    "column": "Profit"
}}
"""

        response = self.llm.generate(prompt)

        # Remove markdown code fences if the model still returns them
        response = response.strip()

        if response.startswith("```"):
            response = response.replace("```json", "")
            response = response.replace("```", "")
            response = response.strip()

        try:
            return json.loads(response)

        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid query plan returned by AI: {response}"
            ) from error