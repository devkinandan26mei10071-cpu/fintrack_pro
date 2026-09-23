# FinTrack Pro - Smart Personal Finance & Budget Intelligence System

> **Course**: Python Essentials (Flipped Course Evaluated Project)  
> **Evaluation Deadline**: Sep 30, 2026, 11:59 PM  
> **Submission Format**: Command-Line Interface (CLI), Public GitHub Repository & PDF Report  

---

## 📖 Overview of the Project

**FinTrack Pro** is an academic-grade, 100% terminal-executable personal finance and budget intelligence system built in pure Python. It empowers students, professionals, and households to manage incomes, control discretionary expenditures, establish strict category-level budget limits, and gain deep statistical insights into cash flow dynamics—all completely offline without relying on third-party cloud trackers or cumbersome graphical user interfaces.

The architecture strictly adheres to object-oriented programming (OOP) principles, clean layered separation of concerns (Models, Storage, Business Services, CLI Presentation, and Utilities), relational persistence via SQLite with ACID transactions and foreign key constraints, robust input validation, and statistical anomaly detection.

---

## 🚀 Key Features

### 1. Transaction & Ledger Engine (Module 1)
- **Double-Entry Style Ledger**: Record, update, delete, and query transactions with date, amount, category, payment method, and description.
- **Smart Auto-Categorizer Algorithm**: Heuristic keyword-matching algorithm that scans transaction semantics to automatically assign categories (e.g., matching "Starbucks" to *Dining Out*, "Uber" to *Transportation*, "Salary" to *Salary & Wages*).
- **Multi-Parameter Search & Filtering**: Filter transactions by date intervals, categories, transaction type (`INCOME` / `EXPENSE`), amount ranges, and textual keywords.

### 2. Budget Intelligence & Multi-Tier Alerts (Module 2)
- **Monthly Category Spending Caps**: Establish monthly budget limits for any expense category.
- **Automated Adherence Classification**:
  - `[OK] SAFE`: Spending is below 80% of category allowance.
  - `[*] WARNING`: Spending is between 80% and 99% of category allowance.
  - `[!] EXCEEDED`: Spending has hit or exceeded 100% of category allowance.
- **Real-Time Variance Computation**: Computes exact dollar balance remaining and percentage utilized.

### 3. Financial Analytics & Statistical Intelligence (Module 3)
- **Macro Cash Flow Summary**: Evaluates total income, total expenditures, net savings, and savings rate percentage.
- **Expense Category Distribution**: Identifies spending hotspots by calculating each category's relative percentage contribution.
- **Descriptive Statistics**: Calculates sample mean, median, standard deviation, and estimated daily spending velocity ($/day).
- **Z-Score Anomaly Spike Detection**: Applies statistical Z-score thresholding (\(z \ge 2.0\)) to identify irregular outlier spending spikes.

### 4. Non-Functional Strengths & Security
- **Performance**: High-speed indexed SQLite queries executing in under 5ms.
- **Security**: Full parameterized SQL queries preventing SQL injection; strict regex sanitization of text inputs.
- **Reliability**: ACID transaction management with automated rollback handling.
- **Usability**: Pure-Python zero-dependency ASCII table renderer (`TableFormatter`) with aligned columns and borders.
- **Auditability**: Complete audit trail stored in SQLite `audit_logs` table tracking all additions, modifications, and deletions.
- **Data Portability**: Bidirectional bulk export and import using standard CSV and JSON formats.

---

## 🛠️ Technologies & Tools Used

- **Core Language**: Python 3.10+ (Standard Library: `sqlite3`, `csv`, `json`, `datetime`, `re`, `logging`, `dataclasses`, `enum`, `typing`, `pathlib`, `unittest`, `argparse`, `math`)
- **Persistence**: Relational SQLite Database (`data/fintrack.db`) with Foreign Keys, Check Constraints, and Indexes.
- **Testing Framework**: Python `unittest` framework (20 automated test cases with isolated in-memory testing).
- **Documentation & Reporting**: Python `reportlab` (for generating the official 15-section PDF report), GitHub Markdown, Mermaid.js diagrams.
- **Version Control**: Git & GitHub CLI.

---

## 📂 Project Architecture

```
fintrack_pro/
│
├── fintrack/
│   ├── __init__.py                  # Package initialization and version metadata
│   ├── models/
│   │   ├── __init__.py
│   │   └── domain.py                # Domain dataclasses: Transaction, Category, Budget, CashFlowSummary
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py              # SQLite connection manager, schema migrations, and indexing
│   │   └── repository.py            # Data Access Object (DAO) pattern with parameterized queries
│   ├── services/
│   │   ├── __init__.py
│   │   ├── transaction_service.py   # Ledger management and heuristic auto-categorizer
│   │   ├── budget_service.py         # Spending limits and three-tier alert intelligence
│   │   ├── analytics_service.py      # Cashflow metrics, statistics, and Z-score anomaly detector
│   │   └── export_service.py         # CSV & JSON bidirectional data interchange
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── interface.py             # Interactive menu system with sub-menus and error recovery
│   │   └── table_formatter.py       # Pure-Python ASCII box-drawing table renderer
│   └── utils/
│       ├── __init__.py
│       ├── validators.py            # Regex validation, bounds checking, and input sanitizers
│       └── logger.py                # Structured rotating file logger (logs/fintrack.log)
│
├── tests/
│   ├── __init__.py
│   ├── test_models.py               # Unit tests for domain models and dataclasses
│   ├── test_validators.py           # Unit tests for input sanitization and boundary rules
│   ├── test_repository.py           # Unit tests for in-memory SQLite DAO and CRUD
│   ├── test_services.py             # Unit tests for business logic, budgets, and analytics
│   └── test_export.py               # Unit tests for CSV/JSON round-trip export & import
│
├── docs/
│   ├── diagrams/                    # Visual diagrams (Architecture, Use Case, Sequence, ER)
│   └── PROJECT_REPORT.md            # Comprehensive 15-section academic project report
│
├── scripts/
│   └── generate_pdf_report.py       # Automated generator for the official PDF report
│
├── data/                            # Local SQLite storage and data exports (CSV, JSON)
├── logs/                            # Rotating runtime execution logs
├── main.py                          # CLI application entrypoint (interactive and argument modes)
├── statement.md                     # Formal Problem Statement and Project Scope document
├── requirements.txt                 # Optional development and reporting dependencies
├── .gitignore                       # Standard Python and runtime file exclusions
└── LICENSE                          # MIT License
```

---

## 💻 Installation & Setup Instructions

Assume a clean environment without prior setup. Follow these step-by-step instructions:

### Step 1: Clone the Repository
```bash
git clone https://github.com/<your-username>/fintrack_pro.git
cd fintrack_pro
```

### Step 2: Verify Python Environment
Ensure Python 3.10 or higher is installed:
```bash
python --version
```

### Step 3: Install Optional Dependencies (For PDF Report Generation)
The core CLI application runs with **zero external pip dependencies**. To enable PDF report compilation:
```bash
pip install -r requirements.txt
```

---

## 🏃 Execution Guide

The application is **100% executable from the command line** and provides two execution modes:

### Mode A: Interactive Terminal Menu
Run the application without flags to enter the interactive console:
```bash
python main.py
```
From here, navigate through formatted menus:
- `1`: Transaction Management (Record, View, Filter, Edit, Delete)
- `2`: Category Management (List categories, Create custom category)
- `3`: Budget Intelligence & Alerts (Set monthly limit, View adherence)
- `4`: Analytics Dashboard (Cashflow summary, Category breakdown, Statistics, Anomalies)
- `5`: Data Portability (Export/Import CSV & JSON)
- `6`: Seed Evaluation Data (Pre-populates sample records)
- `0`: Exit Application

### Mode B: Command-Line Flags (Instant Evaluation)
Execute automated one-shot tasks directly from the shell:

1. **Pre-populate realistic evaluation dataset**:
   ```bash
   python main.py --seed
   ```

2. **Display financial health & budget status summary**:
   ```bash
   python main.py --summary
   ```

3. **Export ledger to CSV**:
   ```bash
   python main.py --export-csv data/ledger_backup.csv
   ```

4. **Export ledger to JSON**:
   ```bash
   python main.py --export-json data/ledger_backup.json
   ```

5. **Generate the Official 15-Section PDF Project Report**:
   ```bash
   python scripts/generate_pdf_report.py
   ```
   *Output saved to `docs/FinTrack_Pro_Project_Report.pdf`.*

---

## 🧪 Testing Instructions

FinTrack Pro includes a comprehensive unit testing suite using Python's standard `unittest` framework. All tests utilize isolated in-memory SQLite databases (`:memory:`), ensuring fast and reproducible execution.

Run the entire test suite with verbose output:
```bash
python -m unittest discover tests -v
```

Expected Output:
```
test_csv_export_and_reimport (test_export.TestExportService.test_csv_export_and_reimport) ... ok
test_json_export (test_export.TestExportService.test_json_export) ... ok
test_budget_status_representation (test_models.TestDomainModels.test_budget_status_representation) ... ok
test_category_model_dict (test_models.TestDomainModels.test_category_model_dict) ... ok
test_transaction_model_dict (test_models.TestDomainModels.test_transaction_model_dict) ... ok
test_transaction_type_enum (test_models.TestDomainModels.test_transaction_type_enum) ... ok
test_add_and_retrieve_category (test_repository.TestFinanceRepository.test_add_and_retrieve_category) ... ok
test_budget_upsert_and_fetch (test_repository.TestFinanceRepository.test_budget_upsert_and_fetch) ... ok
test_schema_and_default_categories (test_repository.TestFinanceRepository.test_schema_and_default_categories) ... ok
test_transaction_crud (test_repository.TestFinanceRepository.test_transaction_crud) ... ok
test_analytics_and_statistics (test_services.TestServices.test_analytics_and_statistics) ... ok
test_auto_detect_category (test_services.TestServices.test_auto_detect_category) ... ok
test_budget_alert_levels (test_services.TestServices.test_budget_alert_levels) ... ok
test_record_transaction_validation_failure (test_services.TestServices.test_record_transaction_validation_failure) ... ok
test_validate_amount_invalid (test_validators.TestValidators.test_validate_amount_invalid) ... ok
test_validate_amount_valid (test_validators.TestValidators.test_validate_amount_valid) ... ok
test_validate_category_name (test_validators.TestValidators.test_validate_category_name) ... ok
test_validate_date_invalid (test_validators.TestValidators.test_validate_date_invalid) ... ok
test_validate_date_valid (test_validators.TestValidators.test_validate_date_valid) ... ok
test_validate_month_year (test_validators.TestValidators.test_validate_month_year) ... ok

----------------------------------------------------------------------
Ran 20 tests in 0.113s

OK
```

---

## 📸 Terminal Output Demos

### 1. Financial Health & Cash Flow Summary (`python main.py --summary`)
```
================ FINANCIAL HEALTH SUMMARY: 2026-09 ================

+----------------------------------------+
|           Cash Flow Overview           |
+-----------------------+----------------+
|         Metric        | Amount / Value |
==========================================
| Total Income          |      $4,570.00 |
| Total Expense         |      $2,499.69 |
| Net Savings           |      $2,070.31 |
| Savings Rate          |          45.3% |
| Transactions Recorded |             14 |
+-----------------------+----------------+

+-------------------------------------------------------------------------------------+
|                               Budget Adherence Status                               |
+-------------------------+-----------+-----------+---------------+--------+----------+
|         Category        | Limit ($) | Spent ($) | Remaining ($) | % Used |  Status  |
=======================================================================================
| Dining Out              |    250.00 |    374.00 |       -124.00 | 149.6% | EXCEEDED |
| Housing & Rent          |   1200.00 |   1100.00 |        100.00 |  91.7% | WARNING  |
| Groceries & Food        |    350.00 |    275.50 |         74.50 |  78.7% | SAFE     |
| Entertainment & Leisure |     50.00 |     19.99 |         30.01 |  40.0% | SAFE     |
+-------------------------+-----------+-----------+---------------+--------+----------+
```

### 2. Expense Category Distribution
```
+---------------------------------------------------------------------------+
|                    Expense Category Distribution: 2026-09                 |
+---------------------------+------------------+------------------+---------+
|      Expense Category     |  Total Spent ($) | % of Total Spend |  Count  |
=============================================================================
| Housing & Rent            |        $1,100.00 |            44.0% |       1 |
| Miscellaneous Expense     |          $450.00 |            18.0% |       1 |
| Dining Out                |          $374.00 |            15.0% |       2 |
| Groceries & Food          |          $275.50 |            11.0% |       2 |
| Education & Books         |           $95.00 |             3.8% |       1 |
| Utilities & Bills         |           $78.20 |             3.1% |       1 |
| Healthcare & Fitness      |           $65.00 |             2.6% |       1 |
| Transportation            |           $42.00 |             1.7% |       1 |
| Entertainment & Leisure   |           $19.99 |             0.8% |       1 |
+---------------------------+------------------+------------------+---------+
```

---

## 📜 Project Report & Submission Document

A complete academic project report covering all 15 required sections (System Architecture, UML Diagrams, ER Schema, Implementation Decisions, Testing Methodology, Challenges, and References) is available in:
- Markdown format: [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md)
- Official Submission PDF: [`docs/FinTrack_Pro_Project_Report.pdf`](docs/FinTrack_Pro_Project_Report.pdf)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
