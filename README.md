# NexaMind

### Privacy-First Financial AI for Excel Analysis

NexaMind is an open-source financial AI copilot that lets users ask natural-language questions about Excel workbooks while keeping sensitive financial data local.

Instead of sending workbook rows or cell values to an LLM, NexaMind sends only the **user's question and workbook schema** to Gemini. Gemini generates a controlled calculation plan, which is validated and executed locally using Pandas.

> **Your financial data never needs to become the AI's context.**

[**Download Latest NexaMind Release**](https://github.com/abhinavwh17/NexaMind/releases/latest)

### Built With

`Python` · `FastAPI` · `Pandas` · `React` · `Gemini` · `PyInstaller` · `GitHub Actions`

---

## Why NexaMind?

Many AI-powered data analysis workflows require data to become part of the AI model's context.

NexaMind takes a different approach.

The LLM acts as a **query planner**, while a trusted local calculation engine performs the actual analysis.

```text
User Question
      │
      ▼
Workbook Schema ──────► Gemini
                         │
                         ▼
                  Calculation Plan
                         │
                         ▼
                  Plan Validation
                         │
                         ▼
Workbook Data ─────► Local Pandas Engine
                         │
                         ▼
                       Result
```

### Sent to Gemini

- User question
- Sheet names
- Column names
- Detected column types

### Not Sent to Gemini

- Workbook file
- Workbook rows
- Cell values
- Financial records

**The AI plans the analysis. NexaMind executes it locally.**

---

## Key Features

### Natural-Language Excel Analysis

Ask questions about financial workbooks using natural language instead of manually creating formulas or writing code.

Examples:

```text
What is the total revenue?

Show total profit by region.

Which customer generated the highest revenue?

Compare issued quantity and produced quantity by customer.

What is the average profit by product?

Show revenue grouped by region and customer.
```

---

### Privacy-First Architecture

Workbook contents are processed locally.

The Gemini API receives only the information required to understand the structure of the workbook and generate a calculation plan.

This separates:

```text
AI Reasoning
     │
     ▼
Calculation Planning
```

from:

```text
Sensitive Data
     │
     ▼
Local Calculation
```

---

### Controlled AI Execution

NexaMind does **not** ask the LLM to generate arbitrary Python code that is then executed.

Instead, Gemini produces a structured calculation plan using operations supported by the NexaMind calculation engine.

For example:

```json
{
  "version": "1.0",
  "calculations": [
    {
      "id": "profit_by_region",
      "operation": "GROUP_BY_METRICS",
      "sheet": "Sales",
      "group_by": ["Region"],
      "metrics": [
        {
          "column": "Profit",
          "aggregation": "SUM",
          "alias": "Total Profit"
        }
      ]
    }
  ]
}
```

The backend validates the plan before executing it against the local workbook.

---

## AI-Powered Excel Analysis

NexaMind uses Gemini to understand the user's analytical intent.

Suppose a workbook contains:

```text
Sheet: Sales

Columns:
Region        string
Customer      string
Revenue       number
Cost          number
Profit        number
Date          datetime
```

The user can ask:

```text
Show total profit by region.
```

Gemini receives the question and schema — **not the rows containing actual revenue or profit values**.

It generates a calculation plan describing the operation NexaMind should perform.

The local Pandas calculation engine then executes that plan.

---

## How NexaMind Works

### 1. Upload an Excel Workbook

The workbook is loaded and processed locally.

Supported formats:

```text
.xlsx
.xls
```

### 2. Extract Workbook Schema

NexaMind identifies metadata such as:

```text
Sheet names
Column names
Detected data types
```

### 3. Ask a Question

For example:

```text
What is total profit by region?
```

### 4. Generate a Calculation Plan

The question and workbook schema are sent to Gemini.

Gemini converts the request into a structured calculation plan.

### 5. Validate the Plan

NexaMind checks the generated plan before execution.

Only supported operations can be executed by the calculation engine.

### 6. Execute Locally

Pandas performs the calculation against the workbook data on the user's machine.

### 7. Present the Result

Results can be displayed as:

- Scalar values
- Grouped results
- Multi-column grouped tables
- Multi-metric tables

Table results can also be exported to Excel or PDF.

---

## Gemini AI Query Planning

Gemini is used as a **planner**, not as the financial calculation engine.

Conceptually:

```text
Question
   +
Workbook Schema
   │
   ▼
Gemini
   │
   ▼
Structured Calculation Plan
```

Gemini does not need access to the underlying workbook records to determine that a question such as:

```text
What is total profit by region?
```

requires something conceptually equivalent to:

```text
GROUP BY Region
SUM Profit
```

The actual aggregation is performed locally.

---

## Local Excel Processing with Pandas

The calculation engine operates on local Pandas DataFrames.

Conceptually:

```text
Excel Workbook
      │
      ▼
Local DataFrame
      │
Calculation Plan
      │
      ▼
Validated Executor
      │
      ▼
Local Result
```

This architecture keeps data processing separate from LLM reasoning.

---

## Supported Financial Calculations

NexaMind's calculation engine supports operations including:

```text
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
```

### Derived Calculations

Supported derived operations include:

```text
ADD
SUBTRACT
MULTIPLY
DIVIDE
PERCENTAGE
```

### Filtering

Supported filtering includes operations such as:

```text
=
!=
>
>=
<
<=

IN
CONTAINS
BETWEEN

IS NULL
IS NOT NULL

LAST_MONTH
THIS_MONTH
```

---

## Multi-Metric Analysis

NexaMind can perform multiple aggregations in a single grouped calculation.

Example question:

```text
Show issued quantity and produced quantity by customer and variety.
```

Example plan:

```json
{
  "operation": "GROUP_BY_METRICS",
  "sheet": "Production",
  "group_by": [
    "Customer",
    "Variety"
  ],
  "metrics": [
    {
      "column": "Issued Qty",
      "aggregation": "SUM",
      "alias": "Issued"
    },
    {
      "column": "Produced Qty",
      "aggregation": "SUM",
      "alias": "Produced"
    }
  ]
}
```

This allows NexaMind to return structured analytical tables rather than only scalar answers.

---

## Example Excel Analysis Questions

Try questions such as:

```text
What is the total revenue?

What is total profit by region?

Which customer generated the highest revenue?

Show monthly revenue totals.

Calculate average profit by product.

Compare revenue and cost by region.

Show the top customers by revenue.

What is the median order value?

How many unique customers are there?

Show issued and produced quantities by customer and variety.
```

---

## Security Model

NexaMind treats LLM output as **untrusted input**.

The model does not receive permission to execute arbitrary operations against workbook data.

The security boundary is:

```text
                UNTRUSTED

                  Gemini
                    │
                    ▼
             Calculation Plan
                    │
              ┌─────▼─────┐
              │ Validator │
              └─────┬─────┘
                    │
                TRUSTED
                    │
                    ▼
            Local Calculation
                    │
                    ▼
                 Workbook
```

NexaMind does not rely on arbitrary LLM-generated Python execution.

Operations outside the supported calculation language are rejected.

Mutation-style operations such as the following are not part of the supported analysis boundary:

```text
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
```

---

## Gemini API Key Security

NexaMind does not ship with a shared Gemini API key.

Each user provides their own Gemini API key.

The key is stored locally using Python's `keyring` integration with the operating system's credential storage.

Depending on the operating system, this typically means:

```text
Windows → Credential Manager
macOS   → Keychain
Linux   → Secret Service / compatible keyring
```

The key is not intended to be stored in browser local storage or embedded in the desktop build.

The application provides settings for configuring or replacing the Gemini connection.

---

## Data Privacy Summary

| Data | Sent to Gemini? |
|---|---|
| User question | Yes |
| Sheet names | Yes |
| Column names | Yes |
| Detected column types | Yes |
| Excel workbook | **No** |
| Workbook rows | **No** |
| Cell values | **No** |
| Financial records | **No** |
| Local calculation results | **No** |

This distinction is important:

**NexaMind is not an offline LLM.**

Gemini is an external AI service and receives the question and workbook schema.

The sensitive workbook contents and locally calculated results remain outside the LLM request.

---

## Result Presentation

Depending on the calculation, NexaMind can present:

### Scalar Results

```text
Total Revenue

₹4,520,000
```

### Grouped Results

```text
Region       Total Profit
--------------------------
North        450,000
South        375,000
East         290,000
West         410,000
```

### Multi-Metric Results

```text
Customer     Issued     Produced
--------------------------------
Customer A   12,500     11,900
Customer B    8,700      8,450
```

---

## Export Results

Structured table results can be exported from the application.

Supported export formats include:

```text
Excel (.xlsx)
PDF (.pdf)
```

This makes calculated results easier to share or use in subsequent workflows without modifying the source workbook.

---

## Download NexaMind

The latest published version is available from GitHub Releases:

[**Download Latest NexaMind Release**](https://github.com/abhinavwh17/NexaMind/releases/latest)

Desktop builds are intended for:

```text
Windows
macOS
```

The goal of the desktop distribution is:

```text
Download
   ↓
Install / Extract
   ↓
Launch NexaMind
   ↓
Local backend starts
   ↓
Browser opens
   ↓
Configure Gemini
   ↓
Analyze workbook
```

End users should not need to install Python, Node.js, React or FastAPI separately when using packaged releases.

---

## Running NexaMind on Windows

Download the Windows package from:

[**NexaMind Releases**](https://github.com/abhinavwh17/NexaMind/releases/latest)

Extract the package and launch:

```text
NexaMind.exe
```

NexaMind starts its local backend and opens the application in the browser.

Unsigned development builds may trigger Windows SmartScreen warnings.

---

## Running NexaMind on macOS

Download the macOS package from:

[**NexaMind Releases**](https://github.com/abhinavwh17/NexaMind/releases/latest)

Install the application and launch:

```text
NexaMind.app
```

### Important

Current development builds may not yet be signed and notarized with an Apple Developer certificate.

macOS Gatekeeper may therefore warn about downloaded builds.

Production-quality public macOS distribution should eventually use:

```text
Build
  ↓
Developer ID Signing
  ↓
Create DMG
  ↓
Sign DMG
  ↓
Apple Notarization
  ↓
Staple
  ↓
Release
```

---

## Development Setup

### Requirements

For local development:

```text
Python 3.12+
Node.js
npm
```

Clone the repository:

```bash
git clone https://github.com/abhinavwh17/NexaMind.git
cd NexaMind
```

---

### Backend Setup

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it.

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Development

Navigate to:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start Vite:

```bash
npm run dev
```

Frontend development server:

```text
http://localhost:5173
```

For production:

```bash
npm run build
```

The production frontend is generated under:

```text
frontend/dist
```

---

## Desktop Packaging

NexaMind uses PyInstaller to package the Python backend and production frontend.

Build the frontend first:

```bash
cd frontend
npm ci
npm run build
cd ..
```

Then build NexaMind:

```bash
pyinstaller --clean NexaMind.spec
```

The generated application is placed under:

```text
dist/
```

The packaged application:

1. Starts FastAPI locally.
2. Serves the production React frontend.
3. Opens NexaMind in the user's browser.

---

## GitHub Actions

NexaMind uses GitHub Actions for desktop build automation.

The desktop pipeline builds platform-specific distributions for:

```text
Windows
macOS
```

The pipeline handles tasks such as:

```text
Frontend dependency installation
React production build
Python environment setup
PyInstaller packaging
Windows artifact generation
macOS application packaging
DMG generation
Artifact upload
```

Workflow artifacts are intended primarily for CI/testing.

Published software should be distributed through **GitHub Releases**.

---

## GitHub Releases

Public versions of NexaMind are distributed through:

[**GitHub Releases**](https://github.com/abhinavwh17/NexaMind/releases)

Recommended release naming:

```text
v1.0.0
v1.1.0
v1.2.0
```

Release assets can include:

```text
NexaMind-Windows.zip
NexaMind-macOS.dmg
```

The permanent latest-release URL is:

```text
https://github.com/abhinavwh17/NexaMind/releases/latest
```

---

## Project Structure

```text
NexaMind/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │
│   ├── llm/
│   │
│   └── services/
│       ├── calculation_service.py
│       ├── dataset_service.py
│       ├── excel_service.py
│       ├── query_planner.py
│       └── settings_service.py
│
├── frontend/
│   ├── src/
│   └── dist/
│
├── tests/
│
├── .github/
│   └── workflows/
│
├── launcher.py
├── NexaMind.spec
├── requirements.txt
└── README.md
```

---

## Technology Stack

### Frontend

```text
React
Vite
JavaScript
HTML
CSS
SheetJS
jsPDF
```

### Backend

```text
Python
FastAPI
Pandas
Uvicorn
```

### AI

```text
Google Gemini
Structured calculation planning
Schema-aware prompting
```

### Desktop

```text
PyInstaller
Windows executable packaging
macOS application / DMG packaging
```

### Security

```text
OS credential storage
Plan validation
Controlled calculation operations
Local workbook execution
```

### DevOps

```text
GitHub
GitHub Actions
Automated desktop builds
Release artifacts
```

---

## Design Philosophy

NexaMind is intentionally focused.

It is not designed to be a general-purpose chatbot.

Its architecture is based on a simple principle:

> **Use AI for reasoning. Use deterministic software for execution.**

For financial analysis this provides a clearer separation between:

```text
Natural-language understanding
            │
            ▼
       AI planning
            │
            ▼
    Validated operation
            │
            ▼
Deterministic local calculation
```

This also makes the system easier to validate, test and extend than executing arbitrary AI-generated code.

---

## Current Limitations

NexaMind is under active development.

Current limitations may include:

- Excel-focused input
- Calculation language supports a defined set of operations
- Complex spreadsheet formulas may require additional operations
- Relative date calculations depend on application/server date behavior
- Desktop builds may not yet be code-signed
- macOS builds may not yet be Apple notarized
- Gemini requires an internet connection
- Gemini requires the user to provide an API key

These constraints are intentional where they help maintain a controlled execution boundary.

---

## Roadmap

Planned improvements include:

- Expanded automated calculation tests
- Security-boundary tests
- Calculation DSL documentation
- Privacy inspection screen
- Sample financial workbook
- Example question library
- Improved desktop installation
- Signed Windows releases
- Signed and notarized macOS releases
- Automated tagged GitHub Releases
- Additional financial calculations
- Improved date handling
- Architecture documentation
- Threat-model documentation

A future local-LLM mode may allow NexaMind to run with providers such as Ollama, enabling a fully local AI planning option.

---

## Security Testing

A major goal of NexaMind is to make the AI execution boundary testable.

Security-oriented tests should verify behavior such as:

```text
Unsupported operation        → rejected
Unknown sheet                → rejected
Unknown column               → rejected
Malformed calculation plan   → rejected
Unexpected Python code       → rejected
Unexpected SQL               → rejected
Mutation request             → rejected
Invalid filter               → rejected
Division by zero             → safely handled
```

This ensures that an incorrect or malicious LLM response cannot automatically become arbitrary workbook execution.

---

## Contributing

NexaMind is an evolving portfolio and open-source project.

Issues, suggestions and pull requests are welcome.

When contributing, please keep the project's core principles in mind:

1. Sensitive workbook data should remain local.
2. LLM output must be treated as untrusted input.
3. Calculations should execute through controlled operations.
4. New capabilities should preserve the privacy boundary.
5. README claims should reflect implemented functionality.

---

## Disclaimer

NexaMind is a software engineering and financial data analysis project.

It does not provide financial, investment, tax or legal advice.

Users are responsible for validating calculations and outputs before using them for business or financial decisions.

---

## Author

**Abhinav Wahi**

Technical Lead · Mobile & Full-Stack Engineer · Applied AI Engineering

GitHub: [@abhinavwh17](https://github.com/abhinavwh17)

---

## License

See the repository's `LICENSE` file for licensing information.
