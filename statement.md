# Project Statement: FinTrack Pro

**Course**: Python Essentials (Flipped Course Evaluation)  
**Project Title**: FinTrack Pro - Smart Personal Finance & Budget Intelligence System  
**Author**: Python Essentials Student  

---

## 1. Problem Statement

Modern individuals, college students, and independent professionals frequently struggle with personal financial management. Without structured tracking, discretionary spending quickly leads to cash flow deficits, neglected savings goals, and unexpected month-end shortfalls. Existing consumer applications often suffer from significant disadvantages:
- They require continuous internet access and transmit sensitive banking information to third-party cloud servers.
- They are weighed down by bloated graphical interfaces, advertisements, and paid subscription paywalls.
- They lack clear, deterministic feedback regarding budget adherence and statistical anomaly detection.

There is a distinct need for a lightweight, secure, 100% terminal-executable personal finance and budget intelligence engine written in pure Python. The system must run locally, guarantee data sovereignty through offline SQLite storage, automate ledger tracking, enforce strict spending caps with proactive multi-tier alerts, and provide actionable financial statistics without requiring any GUI or external network dependencies.

---

## 2. Scope of the Project

The scope of **FinTrack Pro** encompasses an end-to-end command-line financial management platform adhering to strict Python design patterns and standard library modules:

### In-Scope:
- **Ledger Operations**: Comprehensive CRUD management of income and expense transactions with date, amount, category, payment method, and description tracking.
- **Intelligent Auto-Categorization**: Heuristic keyword-matching algorithm that parses description semantics to classify incoming expenses (e.g. transit, food, utilities, wages) automatically.
- **Budget Intelligence & Multi-Tier Alerts**: Category-specific monthly budget caps with automated adherence classification into **SAFE** (<80%), **WARNING** (80%–99%), and **EXCEEDED** (≥100%).
- **Financial Analytics & Distribution**: Automated calculation of macro cash flows (Total Income, Total Expense, Net Savings, Savings Rate %) and category-wise spending proportions.
- **Statistical Anomaly Detection**: Computation of descriptive statistics (mean, median, standard deviation, daily velocity) and algorithmic identification of outlier spending spikes using Z-score thresholding (\(z \ge 2.0\)).
- **Data Portability**: Full bidirectional data synchronization supporting standardized CSV and JSON formats with header validation and error-tolerant parsing.
- **Auditing & Security**: Transaction logging, parameterized SQL queries preventing SQL injection, and a dedicated audit trail tracking all state mutations.

### Out-of-Scope (Future Enhancements):
- Multi-currency live exchange rate fetching (excluded to preserve strict offline execution).
- Multi-user authentication over network sockets (the project focuses on single-user local workstation privacy).
- Native mobile or desktop graphical user interfaces (strictly command-line driven per evaluation rubric).

---

## 3. Target Users

1. **University Students & Young Professionals**:
   Individuals requiring a fast, lightweight, and distraction-free tool to budget semester allowances, track stipends, and manage living costs.
2. **Software Engineers & Terminal Power Users**:
   Developers who prefer terminal-native workflows, keyboard navigation, and local scriptability over cumbersome web or mobile apps.
3. **Privacy-Conscious Individuals**:
   Users who refuse to expose private bank account feeds and transaction histories to cloud-hosted SaaS providers.
4. **Academic Evaluators & Instructors**:
   Educators seeking a comprehensive, reproducible demonstration of Python fundamentals: data structures, object-oriented design, SQLite persistence, unit testing, and CLI architecture.

---

## 4. High-Level Features

| Feature ID | Feature Name | Description |
|---|---|---|
| **F-01** | **Double-Entry Style Ledger Engine** | Add, edit, query, filter, and delete financial records with strict boundary validations. |
| **F-02** | **Heuristic Semantic Categorizer** | Identifies transaction context from descriptive text and maps transactions to categories automatically. |
| **F-03** | **Budget Cap & Threshold Watcher** | Real-time monitoring of monthly spending limits with colorized safe/warning/exceeded status triggers. |
| **F-04** | **Macro Cash Flow Analytics** | Computes monthly income, expenses, net savings, and percentage savings ratios. |
| **F-05** | **Category Distribution Profiler** | Ranks expenses by volume and percentage contribution to overall spending. |
| **F-06** | **Statistical Outlier Detection** | Computes standard deviation and flags abnormal spending anomalies using statistical Z-score analysis. |
| **F-07** | **Zero-Dependency Table Renderer** | Built-in ASCII/Unicode box-drawing console formatter for tables and summaries. |
| **F-08** | **Bidirectional Data Interchange** | Bulk import and export to standard CSV and JSON files for backup and interoperability. |
| **F-09** | **Tamper-Evident Audit Trail** | Logs all administrative updates, additions, and deletions with timestamps into SQLite `audit_logs`. |
| **F-10** | **Automated Evaluation Seeder** | Instant pre-population of realistic demo data via `--seed` flag for rapid evaluation. |
