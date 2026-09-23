"""
FinTrack Pro - Main Application Entrypoint
Provides interactive command-line interface execution and automated CLI arguments.

Usage:
    python main.py                    # Launches interactive console menu
    python main.py --seed             # Seeds sample financial records for evaluation
    python main.py --summary          # Displays cashflow and budget adherence summary
    python main.py --export-csv <f>   # Exports ledger to CSV file
    python main.py --export-json <f>  # Exports ledger to JSON file
"""

import argparse
from datetime import datetime
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fintrack.storage.database import Database
from fintrack.storage.repository import FinanceRepository
from fintrack.services.transaction_service import TransactionService
from fintrack.services.budget_service import BudgetService
from fintrack.services.analytics_service import AnalyticsService
from fintrack.services.export_service import ExportService
from fintrack.cli.interface import CLIInterface
from fintrack.cli.table_formatter import TableFormatter


def build_application(db_path: str = "data/fintrack.db") -> tuple:
    """Dependency injection assembler that wires storage, services, and CLI interface."""
    db = Database(db_path=db_path)
    repo = FinanceRepository(db=db)
    tx_service = TransactionService(repo=repo)
    budget_service = BudgetService(repo=repo)
    analytics_service = AnalyticsService(repo=repo)
    export_service = ExportService(tx_service=tx_service)
    cli = CLIInterface(
        tx_service=tx_service,
        budget_service=budget_service,
        analytics_service=analytics_service,
        export_service=export_service
    )
    return db, repo, tx_service, budget_service, analytics_service, export_service, cli


def main():
    parser = argparse.ArgumentParser(
        description="FinTrack Pro - Smart Personal Finance & Budget Intelligence CLI",
        epilog="Academic Project for Python Essentials Course."
    )
    parser.add_argument("--seed", action="store_true", help="Pre-populate realistic evaluation dataset")
    parser.add_argument("--summary", action="store_true", help="Display monthly cash flow and budget health summary")
    parser.add_argument("--month", type=str, default=datetime.now().strftime("%Y-%m"), help="Target month (YYYY-MM)")
    parser.add_argument("--export-csv", type=str, metavar="FILE", help="Export transaction ledger to CSV")
    parser.add_argument("--export-json", type=str, metavar="FILE", help="Export transaction ledger to JSON")

    args = parser.parse_args()

    db, repo, tx_service, budget_service, analytics_service, export_service, cli = build_application()

    if args.seed:
        cli.seed_demo_data()
        return

    if args.export_csv:
        count = export_service.export_to_csv(args.export_csv)
        print(f"[OK] Exported {count} transactions to CSV: {args.export_csv}")
        return

    if args.export_json:
        count = export_service.export_to_json(args.export_json)
        print(f"[OK] Exported {count} transactions to JSON: {args.export_json}")
        return

    if args.summary:
        month = args.month
        print(f"\n================ FINANCIAL HEALTH SUMMARY: {month} ================\n")
        # Cash flow summary
        cf = analytics_service.get_cashflow_summary(month)
        cf_headers = ["Metric", "Amount / Value"]
        cf_rows = [
            ["Total Income", f"${cf.total_income:,.2f}"],
            ["Total Expense", f"${cf.total_expense:,.2f}"],
            ["Net Savings", f"${cf.net_savings:,.2f}"],
            ["Savings Rate", f"{cf.savings_rate:.1f}%"],
            ["Transactions Recorded", str(cf.transaction_count)]
        ]
        print(TableFormatter.render(cf_headers, cf_rows, ["L", "R"], title="Cash Flow Overview"))

        # Budget adherence
        statuses = budget_service.get_budget_statuses(month)
        if statuses:
            b_headers = ["Category", "Limit ($)", "Spent ($)", "Remaining ($)", "% Used", "Status"]
            b_rows = [
                [s.category_name, f"{s.limit_amount:.2f}", f"{s.spent_amount:.2f}", f"{s.remaining_amount:.2f}", f"{s.percentage_used:.1f}%", s.alert_level.value]
                for s in statuses
            ]
            print("\n" + TableFormatter.render(b_headers, b_rows, ["L", "R", "R", "R", "R", "C"], title="Budget Adherence Status"))
        return

    # Default to interactive mode
    cli.run()


if __name__ == "__main__":
    main()
