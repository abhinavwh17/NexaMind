# NexaMind

### Privacy-First Financial Intelligence

NexaMind is a local-first financial AI copilot that allows users to upload Excel workbooks and ask natural-language questions about their data.

Unlike traditional AI document-analysis workflows, NexaMind does **not send workbook rows, cell values, or uploaded financial files to the AI model**.

Instead, NexaMind sends only the user's question and workbook structure to Gemini. Gemini generates a controlled calculation plan, which is validated and executed locally using Python and Pandas.

> **Your workbook stays on your machine.**
>
> Gemini helps NexaMind understand *what calculation to perform*.
> NexaMind performs the actual calculation locally.

[![Latest Release](https://img.shields.io/github/v/release/abhinavwh17/NexaMind?style=flat-square)](https://github.com/abhinavwh17/NexaMind/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/abhinavwh17/NexaMind/total?style=flat-square)](https://github.com/abhinavwh17/NexaMind/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-lightgrey?style=flat-square)](#running-nexamind)
[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=flat-square)](#technology-stack)
[![Privacy](https://img.shields.io/badge/Data%20Processing-Local-success?style=flat-square)](#privacy-first-architecture)

---

# 📥 Download

The latest desktop builds are available from GitHub Releases:

[**Download Latest NexaMind Release**](https://github.com/abhinavwh17/NexaMind/releases/latest)

Available builds:

```text
Windows
└── NexaMind-Windows.zip
    └── NexaMind.exe

macOS
└── NexaMind-macOS.dmg
    └── NexaMind.app
```

GitHub Releases are intended for users who want to run NexaMind without setting up Python, Node.js, FastAPI, or the development environment.

---

# ✨ Features

- 📊 Analyse Excel workbooks using natural-language questions
- 🔒 Local-first financial data processing
- 🧠 Gemini-powered query planning
- 🧮 Local calculation engine powered by Pandas
- 📈 Grouped and multi-dimensional analysis
- 🔍 Filtering and derived calculations
- 📋 Dynamic table results
- 📥 Export results to Excel
- 📄 Export results to PDF
- 🔑 Secure local Gemini API key storage
- 🖥️ Standalone Windows application
- 🍎 macOS DMG distribution
- ⚙️ Automated desktop builds with GitHub Actions

---

# 🔐 Privacy-First Architecture

Financial data can be highly sensitive.

NexaMind is designed so that the AI model does not need access to the contents of the uploaded workbook.

When a workbook is uploaded:

1. The workbook is loaded locally.
2. NexaMind determines its sheets, columns, and column types.
3. Only this schema metadata and the user's question are sent to Gemini.
4. Gemini returns a structured calculation plan.
5. NexaMind validates the plan.
6. The calculation is executed locally against the workbook using Pandas.
7. The result is displayed in the NexaMind interface.

The actual workbook is never uploaded to Gemini by NexaMind.

## What Leaves Your Device?

| Information | Sent to Gemini? |
|---|:---:|
| Excel workbook | ❌ No |
| Workbook file | ❌ No |
| Financial rows | ❌ No |
| Cell values | ❌ No |
| Calculated intermediate datasets | ❌ No |
| Calculation results | ❌ No |
| User question | ✅ Yes |
| Sheet names | ✅ Yes |
| Column names | ✅ Yes |
| Detected column types | ✅ Yes |

This distinction is important: NexaMind is **local-first**, but Gemini is still an external service used for query planning.

---

# 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │        User         │
                         │                     │
                         │ "Total profit by    │
                         │  customer?"         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    React Frontend   │
                         │                     │
                         │    NexaMind UI      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │                     │
                         │   Local Backend     │
                         └──────────┬──────────┘
                                    │
                       ┌────────────┴────────────┐
                       │                         │
                       ▼                         ▼
              ┌─────────────────┐       ┌─────────────────┐
              │ Excel Workbook  │       │ Workbook Schema │
              │                 │       │                 │
              │ Local Only      │       │ Sheets          │
              │ Pandas/OpenPyXL │       │ Columns         │
              └────────┬────────┘       │ Types           │
                       │                └────────┬────────┘
                       │                         │
                       │                         ▼
                       │                ┌─────────────────┐
                       │                │     Gemini      │
                       │                │  Query Planner  │
                       │                │                 │
                       │                │ Question +      │
                       │                │ Schema Only     │
                       │                └────────┬────────┘
                       │                         │
                       │                         ▼
                       │                ┌─────────────────┐
                       │                │ Structured JSON │
                       │                │ Calculation Plan│
                       │                └────────┬────────┘
                       │                         │
                       │                         ▼
                       │                ┌─────────────────┐
                       │                │ Plan Validation │
                       │                │                 │
                       │                │ Local           │
                       │                └────────┬────────┘
                       │                         │
                       └────────────┬────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Local Calculation   │
                         │ Engine              │
                         │                     │
                         │ Pandas              │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ NexaMind Result     │
                         │                     │
                         │ Answer / Table      │
                         │ Excel / PDF Export  │
                         └─────────────────────┘
```

---

# 🧠 How NexaMind Uses AI

NexaMind does not ask Gemini to calculate directly from financial workbook data.

Gemini acts as a **query planner**.

For example, imagine the workbook contains:

```text
Sheet: Production

Columns:
Party
VARIETY
QUANTITY OF RM
Prod. Qty
```

NexaMind can send schema information similar to:

```json
{
  "sheets": {
    "Production": {
      "columns": [
        {
          "name": "Party",
          "type": "string"
        },
        {
          "name": "VARIETY",
          "type": "string"
        },
        {
          "name": "QUANTITY OF RM",
          "type": "number"
        },
        {
          "name": "Prod. Qty",
          "type": "number"
        }
      ]
    }
  }
}
```

No workbook rows are included.

If the user asks:

```text
Show barley issued, production quantity and balance
by customer and variety.
```

Gemini can produce a controlled plan such as:

```json
{
  "calculations": [
    {
      "id": "calc_1",
      "operation": "GROUP_BY_METRICS",
      "sheet": "Production",
      "group_by": [
        "Party",
        "VARIETY"
      ],
      "metrics": [
        {
          "column": "QUANTITY OF RM",
          "aggregation": "SUM",
          "alias": "Barley Issued"
        },
        {
          "column": "Prod. Qty",
          "aggregation": "SUM",
          "alias": "Production Qty"
        }
      ],
      "derived": [
        {
          "name": "Balance Qty",
          "operation": "SUBTRACT",
          "left": "Barley Issued",
          "right": "Production Qty"
        }
      ]
    }
  ]
}
```

Gemini does **not execute this plan against the workbook**.

NexaMind validates the plan and performs the calculation locally.

---

# 🔄 Query Processing Flow

```text
User Question
      ↓
Workbook Schema
      ↓
Gemini Query Planner
      ↓
Structured Calculation Plan
      ↓
Plan Validation
      ↓
Local Pandas Execution
      ↓
Calculated Result
      ↓
NexaMind UI
```

This separation between **AI planning** and **local execution** is one of the core architectural principles of NexaMind.

---

# 🛡️ Security Design

NexaMind intentionally avoids executing arbitrary AI-generated code.

The AI produces a restricted JSON calculation plan rather than Python, JavaScript, SQL, or shell commands.

The backend validates the requested operations before executing them.

NexaMind does **not** rely on:

- `eval()`
- arbitrary AI-generated Python
- arbitrary shell commands
- AI-generated code execution
- workbook mutation commands

The calculation engine works against local Pandas DataFrames and is designed around explicitly supported read-only operations.

---

# 🧮 Calculation Engine

NexaMind currently supports operations including:

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

## Grouped Analysis

NexaMind supports both single and multi-dimensional grouping.

Example:

```json
{
  "operation": "GROUP_BY_METRICS",
  "group_by": [
    "Party",
    "VARIETY"
  ]
}
```

This allows questions such as:

```text
Show production by customer and variety.
```

---

# 🔎 Filters

The local calculation engine supports controlled filtering operations including:

```text
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
```

Filtering is performed locally against workbook data.

---

# ➗ Derived Calculations

NexaMind can calculate derived metrics from locally calculated values.

Supported operations include:

```text
ADD
SUBTRACT
MULTIPLY
DIVIDE
PERCENTAGE
```

Example:

```text
Barley Issued
-
Production Quantity
=
Balance Quantity
```

---

# 📊 Result Presentation

Depending on the question, NexaMind can return natural-language answers or structured tables.

## Natural-Language Result

```text
The total profit is 16,893,702.26.
```

## Table Result

Grouped and multi-dimensional calculations are displayed as dynamic tables.

Example:

| Party | Variety | Barley Issued | Production Qty | Balance Qty |
|---|---|---:|---:|---:|
| Customer A | 6 ROW | 1,625 | 1,300 | 325 |
| Customer B | 2 ROW | 2,100 | 1,850 | 250 |

---

# 📥 Exporting Results

NexaMind supports client-side result exports.

## Excel

Tabular results can be exported as:

```text
.xlsx
```

## PDF

Tabular results can also be exported as PDF reports.

The export is generated from the already calculated result shown in the application.

The original workbook does not need to be uploaded to an external export service.

---

# 🔑 Gemini API Key

NexaMind does **not** ship with an embedded Gemini API key.

Each user provides their own Gemini API key.

On first launch, NexaMind displays:

```text
Connect Gemini
```

The key is stored using the operating system credential store through Python `keyring`.

Depending on the operating system, this uses facilities such as:

```text
Windows → Windows Credential Manager
macOS   → Keychain
Linux   → supported system keyring backend
```

The application exposes only whether Gemini is configured.

The stored API key itself is not returned to the React frontend.

Users can update their Gemini connection later using:

```text
⚙ Settings
```

---

# 🚀 Running NexaMind

NexaMind can be run as a standalone desktop application.

Python and Node.js are **not required** when using a packaged release.

---

## 🪟 Windows

Download the latest release:

[**Download NexaMind for Windows**](https://github.com/abhinavwh17/NexaMind/releases/latest)

Download:

```text
NexaMind-Windows.zip
```

Extract the ZIP and run:

```text
NexaMind.exe
```

NexaMind will automatically:

```text
Start local FastAPI server
          ↓
http://127.0.0.1:8000
          ↓
Open Google Chrome
          ↓
Display NexaMind
```

If Google Chrome is unavailable, NexaMind can fall back to the system default browser.

---

## 🍎 macOS

Download the latest release:

[**Download NexaMind for macOS**](https://github.com/abhinavwh17/NexaMind/releases/latest)

Download:

```text
NexaMind-macOS.dmg
```

Open the DMG and drag:

```text
NexaMind.app
```

into:

```text
Applications
```

Then launch NexaMind.

NexaMind starts its local backend and opens the application in Google Chrome.

> **Development build notice**
>
> The current macOS distribution is not yet Apple notarized.
> Depending on system security settings, macOS Gatekeeper may display
> a warning when launching a downloaded build.
>
> Apple code signing and notarization are planned for the distribution workflow.

---

# 🧪 Testing NexaMind

After launching NexaMind:

1. Configure your Gemini API key if this is your first launch.
2. Upload an Excel workbook.
3. Wait for NexaMind to prepare the dataset.
4. Enter a question about the workbook.
5. Review the calculated result.
6. Export tabular results to Excel or PDF when required.

Currently supported upload formats:

```text
.xlsx
.xls
```

Example questions:

```text
What is the total profit?
```

```text
Which customer has the highest production quantity?
```

```text
Show total production by customer.
```

```text
Show production quantity by customer and variety.
```

```text
Compare issued quantity and production quantity by customer.
```

```text
What is the balance quantity after subtracting production
from issued quantity?
```

The questions available depend on the structure and columns in the uploaded workbook.

---

# 💻 Development Setup

## Requirements

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

## Backend Setup

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

---

## Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

During development:

```text
React / Vite
http://localhost:5173

        ↓

FastAPI
http://127.0.0.1:8000
```

---

# 📦 Building the Frontend

Create the production React build:

```bash
cd frontend
npm run build
```

Vite generates:

```text
frontend/dist/
```

The production FastAPI application serves this directory directly.

Production therefore uses:

```text
Browser
   ↓
http://127.0.0.1:8000
   ↓
FastAPI
   ├── API
   └── React frontend
```

---

# 🖥️ Building the Desktop Application

NexaMind uses PyInstaller to package the Python backend, application launcher, dependencies, and production frontend.

From the project root:

```bash
pyinstaller --clean NexaMind.spec
```

The resulting desktop executable is created under:

```text
dist/
```

The desktop launcher:

```text
launcher.py
```

is responsible for:

```text
Launch NexaMind
      ↓
Start FastAPI
      ↓
Serve bundled React application
      ↓
Open Chrome
```

---

# ⚙️ GitHub Actions

NexaMind uses GitHub Actions to build desktop applications automatically.

The CI pipeline performs:

```text
Checkout source
      ↓
Install Node.js
      ↓
npm ci
      ↓
Build React
      ↓
Install Python
      ↓
Install backend dependencies
      ↓
PyInstaller
      ↓
Package desktop application
      ↓
Upload build artifact
```

Platform-specific GitHub runners are used because PyInstaller builds applications for the operating system on which it runs.

## Windows Build

```text
windows-latest
      ↓
NexaMind.exe
      ↓
NexaMind-Windows.zip
```

## macOS Build

```text
macos-latest
      ↓
NexaMind
      ↓
NexaMind.app
      ↓
NexaMind-macOS.dmg
```

No Gemini API key is embedded into the generated application.

---

# 🏷️ GitHub Releases

NexaMind uses GitHub Releases as the public distribution channel for packaged desktop builds.

A release can contain:

```text
Release v1.0.0

Assets
├── NexaMind-Windows.zip
└── NexaMind-macOS.dmg
```

Users can always access the newest version from:

```text
https://github.com/abhinavwh17/NexaMind/releases/latest
```

## Recommended Release Workflow

```text
Development
     ↓
Merge into main
     ↓
Create version tag
     ↓
v1.0.0
     ↓
GitHub Actions
     ↓
Build Windows + macOS
     ↓
Create GitHub Release
     ↓
Attach ZIP + DMG
     ↓
Users download from Releases
```

Example version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The release pipeline can then create a GitHub Release and attach both desktop packages automatically.

---

# 📁 Project Structure

```text
NexaMind/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │
│   ├── llm/
│   │   └── client.py
│   │
│   ├── services/
│   │   ├── calculation_service.py
│   │   ├── dataset_service.py
│   │   ├── excel_service.py
│   │   ├── query_planner.py
│   │   └── settings_service.py
│   │
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   └── App.css
│   │
│   ├── package.json
│   └── package-lock.json
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

# 🧰 Technology Stack

## Frontend

- React
- Vite
- JavaScript
- SheetJS (`xlsx`)
- jsPDF
- jsPDF-AutoTable

## Backend

- Python
- FastAPI
- Pandas
- OpenPyXL

## AI

- Google Gemini
- Structured JSON calculation planning

## Security

- Python `keyring`
- OS-native credential storage
- Controlled calculation DSL
- Plan validation
- Local workbook processing

## Desktop Distribution

- PyInstaller
- GitHub Actions
- Windows executable packaging
- macOS application packaging
- DMG generation

---

# 🎯 Design Philosophy

NexaMind separates:

```text
AI reasoning about the question
```

from:

```text
execution against sensitive financial data
```

A traditional AI analysis workflow may look like:

```text
Workbook
   ↓
AI Provider
   ↓
Analysis
```

NexaMind instead uses:

```text
              Question + Schema
                     │
                     ▼
                 AI Planner
                     │
                     ▼
             Calculation Plan
                     │
                     ▼

Workbook ─────► Local Calculation Engine
                     │
                     ▼
                   Result
```

This allows AI to interpret natural-language questions without requiring the AI model to directly access the underlying workbook records.

---

# 🔒 Core Privacy Principle

```text
AI decides WHAT calculation is required.

NexaMind decides HOW it is safely executed.

Your workbook data stays local.
```

The workbook itself is never intentionally included in the Gemini request.

The external AI service receives only the information required to understand the workbook structure and generate a calculation plan.

---

# ⚠️ Current Limitations

NexaMind is under active development.

Current limitations include:

- Excel-focused workbook analysis
- `.xlsx` and `.xls` input support
- Gemini is currently the supported AI planning provider
- Analysis is limited to operations supported by NexaMind's calculation DSL
- Complex or irregular workbook layouts may require additional normalization
- macOS releases are not yet Apple notarized
- The local backend remains active while NexaMind is running
- Multi-file analytical relationships are still evolving
- Some advanced date semantics require further refinement

NexaMind should currently be considered a development and portfolio project rather than a production financial decision-making system.

---

# 🗺️ Roadmap

Planned improvements include:

- Expanded financial calculation operations
- Improved workbook structure detection
- More advanced date-based analysis
- Multi-workbook analysis
- Formula-aware financial analysis
- Charts and visual analytics
- Improved desktop application lifecycle management
- Single-instance desktop handling
- Signed Windows builds
- Apple Developer ID signing
- Apple notarization
- Automated GitHub Releases
- Improved automated testing
- Additional privacy and security controls
- Optional support for additional LLM providers

---

# 🤝 Contributing

Contributions, ideas, and technical feedback are welcome.

When contributing, please preserve NexaMind's core architectural principle:

> **Sensitive workbook data should remain local whenever possible, and AI-generated instructions must be validated before execution.**

---

# 📄 Disclaimer

NexaMind is an experimental financial data analysis tool.

Results should be independently verified before being used for financial, accounting, regulatory, investment, or other high-impact decisions.

Users are responsible for reviewing the privacy policies and terms applicable to any external AI service they configure with NexaMind.

---

# NexaMind

### Financial Intelligence, with your data staying under your control.

**Local data. AI-assisted planning. Controlled execution.**
