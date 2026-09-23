"""
Interactive terminal user interface for FinTrack Pro.
Provides structured menus, interactive prompts, colorized feedback, and comprehensive workflows.
"""

from datetime import datetime
import sys
from typing import Optional

from fintrack.cli.table_formatter import TableFormatter
from fintrack.models.domain import TransactionType, AlertLevel
from fintrack.services.transaction_service import TransactionService
from fintrack.services.budget_service import BudgetService
from fintrack.services.analytics_service import AnalyticsService
from fintrack.services.export_service import ExportService
from fintrack.utils.validators import ValidationError
from fintrack.utils.logger import app_logger


class CLIInterface:
    """Manages the interactive terminal menu system and user commands."""

    def __init__(
        self,
        tx_service: TransactionService,
        budget_service: BudgetService,
        analytics_service: AnalyticsService,
        export_service: ExportService
    ):
        self.tx_service = tx_service
        self.budget_service = budget_service
        self.analytics_service = analytics_service
        self.export_service = export_service

    def print_banner(self) -> None:
        """Displays application header and branding."""
        print("\n" + "=" * 65)
        print("  FINTRACK PRO - Personal Finance & Budget Intelligence System")
        print("         Python Essentials - Evaluated Course Project")
        print("=" * 65)

    def run(self) -> None:
        """Main interaction loop."""
        self.print_banner()
        while True:
            try:
                print("\n=== MAIN MENU ===")
                print("1. [Ledger] Transaction Management")
                print("2. [Categories] View & Add Categories")
                print("3. [Budgets] Spending Limits & Adherence Alerts")
                print("4. [Analytics] Financial Reports & Anomaly Detection")
                print("5. [Data Portability] CSV & JSON Import / Export")
                print("6. [Demo] Seed Sample Evaluation Data")
                print("0. Exit Application")

                choice = input("\nSelect an option [0-6]: ").strip()
                if choice == "1":
                    self.menu_transactions()
                elif choice == "2":
                    self.menu_categories()
                elif choice == "3":
                    self.menu_budgets()
                elif choice == "4":
                    self.menu_analytics()
                elif choice == "5":
                    self.menu_portability()
                elif choice == "6":
                    self.seed_demo_data()
                elif choice in ("0", "exit", "quit", "q"):
                    print("\nThank you for using FinTrack Pro. Exiting.\n")
                    break
                else:
                    print("Invalid selection. Please choose an option between 0 and 6.")
            except KeyboardInterrupt:
                print("\n\nOperation interrupted by user. Exiting.\n")
                break
            except Exception as e:
                app_logger.exception("Unexpected error in main CLI loop")
                print(f"\n[ERROR] An unexpected error occurred: {e}")

    # ==========================================
    # MENU 1: TRANSACTIONS
    # ==========================================
    def menu_transactions(self) -> None:
        while True:
            print("\n--- TRANSACTION MANAGEMENT ---")
            print("1. Record New Transaction")
            print("2. View Recent Transactions")
            print("3. Filter / Search Transactions")
            print("4. Edit a Transaction")
            print("5. Delete a Transaction")
            print("0. Return to Main Menu")

            choice = input("Select option [0-5]: ").strip()
            if choice == "1":
                self.action_record_transaction()
            elif choice == "2":
                self.action_view_transactions()
            elif choice == "3":
                self.action_filter_transactions()
            elif choice == "4":
                self.action_edit_transaction()
            elif choice == "5":
                self.action_delete_transaction()
            elif choice == "0":
                break
            else:
                print("Invalid choice.")

    def action_record_transaction(self) -> None:
        print("\n--- Record New Transaction ---")
        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            date_input = input(f"Date (YYYY-MM-DD) [default: {today_str}]: ").strip() or today_str
            amount_input = input("Amount ($): ").strip()
            type_input = input("Type (1 for EXPENSE, 2 for INCOME) [1]: ").strip()
            trans_type = TransactionType.INCOME if type_input == "2" else TransactionType.EXPENSE

            print(f"\nAvailable Categories for {trans_type.value}:")
            cats = self.tx_service.list_categories(trans_type)
            for c in cats:
                print(f"  [{c.id}] {c.name}")

            cat_id_input = input("Category ID (or press Enter to auto-detect from description): ").strip()
            cat_id = int(cat_id_input) if cat_id_input.isdigit() else None

            desc_input = input("Description: ").strip()
            method_input = input("Payment Method [Cash/Credit Card/Debit Card/UPI/Bank Transfer] (default: Cash): ").strip() or "Cash"

            tx = self.tx_service.record_transaction(
                date=date_input,
                amount=amount_input,
                trans_type=trans_type,
                category_id=cat_id,
                description=desc_input,
                payment_method=method_input
            )

            print(f"\n[SUCCESS] Transaction #{tx.id} recorded successfully! Assigned Category: '{tx.category_name}'")
        except ValidationError as ve:
            print(f"\n[VALIDATION ERROR] {ve}")
        except Exception as e:
            print(f"\n[ERROR] Could not record transaction: {e}")

    def action_view_transactions(self, limit: int = 20) -> None:
        transactions = self.tx_service.list_transactions(limit=limit)
        headers = ["ID", "Date", "Type", "Category", "Amount ($)", "Method", "Description"]
        rows = [
            [
                t.id,
                t.date,
                t.type.value,
                t.category_name,
                f"{t.amount:.2f}",
                t.payment_method,
                t.description[:25]
            ]
            for t in transactions
        ]
        table = TableFormatter.render(
            headers=headers,
            rows=rows,
            alignments=["R", "L", "L", "L", "R", "L", "L"],
            title=f"Recent Transactions (Showing up to {limit})"
        )
        print("\n" + table)

    def action_filter_transactions(self) -> None:
        print("\n--- Filter / Search Transactions (leave empty to skip filter) ---")
        start = input("Start Date (YYYY-MM-DD): ").strip() or None
        end = input("End Date (YYYY-MM-DD): ").strip() or None
        type_str = input("Type (INCOME/EXPENSE): ").strip() or None
        query = input("Keyword search in description/category: ").strip() or None
        min_amt = input("Minimum amount: ").strip()
        min_float = float(min_amt) if min_amt else None

        results = self.tx_service.list_transactions(
            start_date=start,
            end_date=end,
            trans_type=type_str,
            search_query=query,
            min_amount=min_float,
            limit=50
        )

        headers = ["ID", "Date", "Type", "Category", "Amount ($)", "Method", "Description"]
        rows = [
            [t.id, t.date, t.type.value, t.category_name, f"{t.amount:.2f}", t.payment_method, t.description[:30]]
            for t in results
        ]
        print("\n" + TableFormatter.render(headers, rows, ["R", "L", "L", "L", "R", "L", "L"], title="Search Results"))

    def action_edit_transaction(self) -> None:
        tx_id_str = input("Enter Transaction ID to edit: ").strip()
        if not tx_id_str.isdigit():
            print("Invalid ID.")
            return

        tx = self.tx_service.get_transaction(int(tx_id_str))
        if not tx:
            print("Transaction not found.")
            return

        print(f"\nEditing Transaction #{tx.id} [Date: {tx.date}, Amount: ${tx.amount:.2f}, Type: {tx.type.value}]")
        print("Leave blank to keep existing value.")
        new_date = input(f"New Date [{tx.date}]: ").strip() or None
        new_amount = input(f"New Amount [${tx.amount:.2f}]: ").strip() or None
        new_desc = input(f"New Description [{tx.description}]: ").strip() or None
        new_method = input(f"New Payment Method [{tx.payment_method}]: ").strip() or None

        try:
            updated = self.tx_service.modify_transaction(
                tx_id=tx.id, # type: ignore
                date=new_date,
                amount=new_amount,
                description=new_desc,
                payment_method=new_method
            )
            print(f"[SUCCESS] Transaction #{updated.id} successfully updated.")
        except ValidationError as ve:
            print(f"[VALIDATION ERROR] {ve}")

    def action_delete_transaction(self) -> None:
        tx_id_str = input("Enter Transaction ID to delete: ").strip()
        if not tx_id_str.isdigit():
            print("Invalid ID.")
            return
        tx_id = int(tx_id_str)
        confirm = input(f"Are you sure you want to delete transaction #{tx_id}? (y/N): ").strip().lower()
        if confirm == "y":
            deleted = self.tx_service.remove_transaction(tx_id)
            if deleted:
                print(f"[SUCCESS] Transaction #{tx_id} deleted.")
            else:
                print("Transaction not found or already deleted.")

    # ==========================================
    # MENU 2: CATEGORIES
    # ==========================================
    def menu_categories(self) -> None:
        while True:
            print("\n--- CATEGORY MANAGEMENT ---")
            print("1. List All Categories")
            print("2. Add New Category")
            print("0. Return to Main Menu")

            c = input("Select option [0-2]: ").strip()
            if c == "1":
                cats = self.tx_service.list_categories()
                headers = ["ID", "Category Name", "Type", "Description"]
                rows = [[cat.id, cat.name, cat.type.value, cat.description] for cat in cats]
                print("\n" + TableFormatter.render(headers, rows, ["R", "L", "L", "L"], title="Configured Categories"))
            elif c == "2":
                try:
                    name = input("Category Name: ").strip()
                    type_str = input("Type (1 for EXPENSE, 2 for INCOME) [1]: ").strip()
                    cat_type = TransactionType.INCOME if type_str == "2" else TransactionType.EXPENSE
                    desc = input("Description: ").strip()
                    cat = self.tx_service.create_category(name, cat_type, desc)
                    print(f"[SUCCESS] Category '{cat.name}' created with ID {cat.id}.")
                except ValidationError as ve:
                    print(f"[VALIDATION ERROR] {ve}")
            elif c == "0":
                break

    # ==========================================
    # MENU 3: BUDGETS
    # ==========================================
    def menu_budgets(self) -> None:
        while True:
            print("\n--- BUDGET INTELLIGENCE & ALERTS ---")
            print("1. Set / Update Category Budget Limit")
            print("2. View Monthly Budget Status & Adherence Alerts")
            print("3. Delete a Budget")
            print("0. Return to Main Menu")

            c = input("Select option [0-3]: ").strip()
            if c == "1":
                self.action_set_budget()
            elif c == "2":
                self.action_view_budgets()
            elif c == "3":
                self.action_delete_budget()
            elif c == "0":
                break

    def action_set_budget(self) -> None:
        print("\n--- Set Monthly Budget Limit ---")
        current_month = datetime.now().strftime("%Y-%m")
        month = input(f"Month (YYYY-MM) [default: {current_month}]: ").strip() or current_month

        print("\nExpense Categories:")
        cats = self.tx_service.list_categories(TransactionType.EXPENSE)
        for cat in cats:
            print(f"  [{cat.id}] {cat.name}")

        cat_id_str = input("Category ID: ").strip()
        if not cat_id_str.isdigit():
            print("Invalid ID.")
            return

        limit_str = input("Monthly Spending Limit ($): ").strip()
        try:
            b = self.budget_service.set_category_budget(int(cat_id_str), month, limit_str)
            print(f"[SUCCESS] Budget limit of ${b.limit_amount:.2f} established for '{b.category_name}' in {month}.")
        except ValidationError as ve:
            print(f"[VALIDATION ERROR] {ve}")

    def action_view_budgets(self) -> None:
        current_month = datetime.now().strftime("%Y-%m")
        month = input(f"Month to inspect (YYYY-MM) [default: {current_month}]: ").strip() or current_month

        statuses = self.budget_service.get_budget_statuses(month)
        if not statuses:
            print(f"\nNo budget limits configured for {month}. Use option 1 to set one.")
            return

        headers = ["Category", "Month", "Limit ($)", "Spent ($)", "Remaining ($)", "% Used", "Status Alert"]
        rows = []
        for s in statuses:
            alert_str = s.alert_level.value
            if s.alert_level == AlertLevel.EXCEEDED:
                alert_str = "[!] EXCEEDED"
            elif s.alert_level == AlertLevel.WARNING:
                alert_str = "[*] WARNING"
            else:
                alert_str = "[OK] SAFE"

            rows.append([
                s.category_name,
                s.month,
                f"{s.limit_amount:.2f}",
                f"{s.spent_amount:.2f}",
                f"{s.remaining_amount:.2f}",
                f"{s.percentage_used:.1f}%",
                alert_str
            ])

        print("\n" + TableFormatter.render(headers, rows, ["L", "C", "R", "R", "R", "R", "C"], title=f"Budget Adherence Report - {month}"))

    def action_delete_budget(self) -> None:
        month = input("Month (YYYY-MM): ").strip()
        cat_id_str = input("Category ID to remove budget for: ").strip()
        if not cat_id_str.isdigit():
            print("Invalid ID.")
            return
        deleted = self.budget_service.remove_budget(int(cat_id_str), month)
        if deleted:
            print("[SUCCESS] Budget removed.")
        else:
            print("Budget not found.")

    # ==========================================
    # MENU 4: ANALYTICS & REPORTS
    # ==========================================
    def menu_analytics(self) -> None:
        current_month = datetime.now().strftime("%Y-%m")
        month = input(f"\nSelect Month for Financial Analytics (YYYY-MM) [default: {current_month}]: ").strip() or current_month

        while True:
            print(f"\n--- ANALYTICS DASHBOARD ({month}) ---")
            print("1. Macro Cash Flow Summary (Income, Expense, Net Savings, Savings Rate)")
            print("2. Category Spending Breakdown & Share")
            print("3. Descriptive Statistics & Daily Velocity")
            print("4. Spending Anomaly Detection (Statistical Outliers)")
            print("0. Return to Main Menu")

            c = input("Select option [0-4]: ").strip()
            if c == "1":
                summary = self.analytics_service.get_cashflow_summary(month)
                headers = ["Metric", "Value"]
                rows = [
                    ["Evaluation Month", summary.month],
                    ["Total Income Recorded", f"${summary.total_income:,.2f}"],
                    ["Total Expenses Recorded", f"${summary.total_expense:,.2f}"],
                    ["Net Savings", f"${summary.net_savings:,.2f}"],
                    ["Savings Rate", f"{summary.savings_rate:.1f}%"],
                    ["Total Transactions Count", str(summary.transaction_count)]
                ]
                print("\n" + TableFormatter.render(headers, rows, ["L", "R"], title=f"Cash Flow Health Report: {month}"))
            elif c == "2":
                breakdown = self.analytics_service.get_category_breakdown(month)
                headers = ["Expense Category", "Total Spent ($)", "% of Total Spend", "Transactions"]
                rows = [
                    [item.category_name, f"${item.total_amount:,.2f}", f"{item.percentage_of_total:.1f}%", item.transaction_count]
                    for item in breakdown
                ]
                print("\n" + TableFormatter.render(headers, rows, ["L", "R", "R", "R"], title=f"Expense Category Distribution: {month}"))
            elif c == "3":
                stats = self.analytics_service.get_statistical_metrics(month)
                headers = ["Statistical Parameter", "Value"]
                rows = [
                    ["Analyzed Month", stats["month"]],
                    ["Total Expense Count", str(stats["count"])],
                    ["Mean Transaction Size", f"${stats['mean']:,.2f}"],
                    ["Median Transaction Size", f"${stats['median']:,.2f}"],
                    ["Standard Deviation", f"${stats['std_dev']:,.2f}"],
                    ["Lowest Expense", f"${stats['min']:,.2f}"],
                    ["Highest Expense", f"${stats['max']:,.2f}"],
                    ["Estimated Daily Spend Velocity", f"${stats['daily_velocity']:,.2f} / day"]
                ]
                print("\n" + TableFormatter.render(headers, rows, ["L", "R"], title="Expense Distribution Statistics"))
            elif c == "4":
                anomalies = self.analytics_service.detect_spending_anomalies(month)
                if not anomalies:
                    print(f"\n[OK] No unusual spending spikes detected for {month} (or insufficient sample size < 5).")
                else:
                    headers = ["ID", "Date", "Category", "Amount ($)", "Z-Score", "Deviation Above Mean ($)", "Description"]
                    rows = [
                        [a["id"], a["date"], a["category"], f"${a['amount']:,.2f}", f"+{a['z_score']}σ", f"+${a['deviation_over_mean']:,.2f}", a["description"][:25]]
                        for a in anomalies
                    ]
                    print("\n" + TableFormatter.render(headers, rows, ["R", "L", "L", "R", "R", "R", "L"], title="Spike Detection (Transactions > 2.0 Std Dev)"))
            elif c == "0":
                break

    # ==========================================
    # MENU 5: PORTABILITY
    # ==========================================
    def menu_portability(self) -> None:
        while True:
            print("\n--- DATA PORTABILITY & SYNCHRONIZATION ---")
            print("1. Export All Transactions to CSV")
            print("2. Export All Transactions to JSON")
            print("3. Bulk Import Transactions from CSV")
            print("0. Return to Main Menu")

            c = input("Select option [0-3]: ").strip()
            if c == "1":
                path = input("CSV destination path [data/export_transactions.csv]: ").strip() or "data/export_transactions.csv"
                count = self.export_service.export_to_csv(path)
                print(f"[SUCCESS] Exported {count} transactions to '{path}'.")
            elif c == "2":
                path = input("JSON destination path [data/export_transactions.json]: ").strip() or "data/export_transactions.json"
                count = self.export_service.export_to_json(path)
                print(f"[SUCCESS] Exported {count} transactions to '{path}'.")
            elif c == "3":
                path = input("CSV source file to import: ").strip()
                try:
                    s_count, errors = self.export_service.import_from_csv(path)
                    print(f"\n[SUCCESS] Imported {s_count} transactions successfully.")
                    if errors:
                        print(f"[WARNING] {len(errors)} rows had errors:")
                        for err in errors[:5]:
                            print(f"  - {err}")
                except Exception as e:
                    print(f"[ERROR] Import failed: {e}")
            elif c == "0":
                break

    # ==========================================
    # MENU 6: DEMO DATA SEEDING
    # ==========================================
    def seed_demo_data(self) -> None:
        """Injects realistic transactions and budgets across two months for instant evaluation."""
        from datetime import datetime
        print("\nSeeding realistic financial data for evaluation...")
        current_month = datetime.now().strftime("%Y-%m")
        # Current month and past month
        sample_records = [
            # Incomes
            (f"{current_month}-01", 3800.00, "INCOME", "Salary & Wages", "Monthly core salary direct deposit", "Bank Transfer"),
            (f"{current_month}-10", 650.00, "INCOME", "Freelancing & Side Hustle", "Python consulting project milestone", "UPI"),
            (f"{current_month}-15", 120.00, "INCOME", "Investments & Dividends", "Quarterly index fund dividend payout", "Bank Transfer"),
            # Expenses
            (f"{current_month}-02", 1100.00, "EXPENSE", "Housing & Rent", "Apartment monthly rent", "Bank Transfer"),
            (f"{current_month}-03", 145.50, "EXPENSE", "Groceries & Food", "Trader Joe's weekly pantry restock", "Debit Card"),
            (f"{current_month}-05", 42.00, "EXPENSE", "Transportation", "Metro card monthly pass refill", "Credit Card"),
            (f"{current_month}-07", 78.20, "EXPENSE", "Utilities & Bills", "High-speed optical fiber internet bill", "Credit Card"),
            (f"{current_month}-09", 54.00, "EXPENSE", "Dining Out", "Dinner with colleagues at Italian bistro", "Credit Card"),
            (f"{current_month}-12", 130.00, "EXPENSE", "Groceries & Food", "Costco household essentials and dairy", "Debit Card"),
            (f"{current_month}-14", 19.99, "EXPENSE", "Entertainment & Leisure", "Netflix and Spotify subscriptions", "Credit Card"),
            (f"{current_month}-16", 65.00, "EXPENSE", "Healthcare & Fitness", "Gym membership and protein shaker", "Debit Card"),
            (f"{current_month}-18", 320.00, "EXPENSE", "Dining Out", "Celebration party dinner (budget warning)", "Credit Card"),
            (f"{current_month}-20", 450.00, "EXPENSE", "Miscellaneous Expense", "Emergency laptop monitor repair (statistical spike)", "Credit Card"),
            (f"{current_month}-22", 95.00, "EXPENSE", "Education & Books", "Python Systems Programming reference book", "Debit Card"),
        ]

        for date_s, amt, t_type, cat_name, desc, method in sample_records:
            try:
                self.tx_service.record_transaction(
                    date=date_s,
                    amount=amt,
                    trans_type=t_type,
                    category_name=cat_name,
                    description=desc,
                    payment_method=method
                )
            except Exception:
                pass

        # Setup sample budgets
        groceries = self.tx_service.repo.get_category_by_name("Groceries & Food")
        dining = self.tx_service.repo.get_category_by_name("Dining Out")
        housing = self.tx_service.repo.get_category_by_name("Housing & Rent")
        ent = self.tx_service.repo.get_category_by_name("Entertainment & Leisure")

        if groceries:
            self.budget_service.set_category_budget(groceries.id, current_month, 350.00) # type: ignore
        if dining:
            self.budget_service.set_category_budget(dining.id, current_month, 250.00) # type: ignore
        if housing:
            self.budget_service.set_category_budget(housing.id, current_month, 1200.00) # type: ignore
        if ent:
            self.budget_service.set_category_budget(ent.id, current_month, 50.00) # type: ignore

        print("[SUCCESS] Evaluation demo data seeded! You can now view transactions, budget alerts, and analytics.")
