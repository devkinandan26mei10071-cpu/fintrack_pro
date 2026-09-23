"""
Unit tests for business logic services: TransactionService, BudgetService, and AnalyticsService.
"""

import unittest
from fintrack.models.domain import TransactionType, AlertLevel
from fintrack.storage.database import Database
from fintrack.storage.repository import FinanceRepository
from fintrack.services.transaction_service import TransactionService
from fintrack.services.budget_service import BudgetService
from fintrack.services.analytics_service import AnalyticsService
from fintrack.utils.validators import ValidationError


class TestServices(unittest.TestCase):

    def setUp(self):
        self.db = Database(db_path=":memory:")
        self.repo = FinanceRepository(self.db)
        self.tx_service = TransactionService(self.repo)
        self.budget_service = BudgetService(self.repo)
        self.analytics_service = AnalyticsService(self.repo)

    def test_auto_detect_category(self):
        # "Starbucks iced latte" -> Dining Out
        tx = self.tx_service.record_transaction(
            date="2026-09-01",
            amount=6.75,
            trans_type=TransactionType.EXPENSE,
            description="Starbucks iced caramel macchiato"
        )
        self.assertEqual(tx.category_name, "Dining Out")

        # "Uber ride to airport" -> Transportation
        tx2 = self.tx_service.record_transaction(
            date="2026-09-02",
            amount=38.50,
            trans_type=TransactionType.EXPENSE,
            description="Uber cab to terminal"
        )
        self.assertEqual(tx2.category_name, "Transportation")

    def test_record_transaction_validation_failure(self):
        with self.assertRaises(ValidationError):
            self.tx_service.record_transaction(
                date="invalid-date",
                amount=100.0,
                trans_type=TransactionType.EXPENSE
            )

        with self.assertRaises(ValidationError):
            self.tx_service.record_transaction(
                date="2026-09-01",
                amount=-50.0,
                trans_type=TransactionType.EXPENSE
            )

    def test_budget_alert_levels(self):
        cat = self.repo.get_category_by_name("Dining Out")
        self.assertIsNotNone(cat)

        # Set budget limit of $100 for September 2026
        self.budget_service.set_category_budget(cat.id, "2026-09", 100.00)

        # Scenario 1: Spend $50 -> SAFE (50%)
        self.tx_service.record_transaction(date="2026-09-05", amount=50.00, trans_type=TransactionType.EXPENSE, category_id=cat.id)
        statuses = self.budget_service.get_budget_statuses("2026-09")
        self.assertEqual(statuses[0].alert_level, AlertLevel.SAFE)
        self.assertEqual(statuses[0].percentage_used, 50.0)

        # Scenario 2: Spend another $35 ($85 total) -> WARNING (85%)
        self.tx_service.record_transaction(date="2026-09-10", amount=35.00, trans_type=TransactionType.EXPENSE, category_id=cat.id)
        statuses = self.budget_service.get_budget_statuses("2026-09")
        self.assertEqual(statuses[0].alert_level, AlertLevel.WARNING)
        self.assertEqual(statuses[0].percentage_used, 85.0)

        # Scenario 3: Spend another $20 ($105 total) -> EXCEEDED (105%)
        self.tx_service.record_transaction(date="2026-09-12", amount=20.00, trans_type=TransactionType.EXPENSE, category_id=cat.id)
        statuses = self.budget_service.get_budget_statuses("2026-09")
        self.assertEqual(statuses[0].alert_level, AlertLevel.EXCEEDED)
        self.assertEqual(statuses[0].percentage_used, 105.0)

    def test_analytics_and_statistics(self):
        # Populate controlled records for month 2026-09
        self.tx_service.record_transaction(date="2026-09-01", amount=3000.00, trans_type=TransactionType.INCOME, category_name="Salary & Wages")
        self.tx_service.record_transaction(date="2026-09-02", amount=50.00, trans_type=TransactionType.EXPENSE, category_name="Groceries & Food")
        self.tx_service.record_transaction(date="2026-09-03", amount=50.00, trans_type=TransactionType.EXPENSE, category_name="Groceries & Food")
        self.tx_service.record_transaction(date="2026-09-04", amount=50.00, trans_type=TransactionType.EXPENSE, category_name="Groceries & Food")
        self.tx_service.record_transaction(date="2026-09-05", amount=50.00, trans_type=TransactionType.EXPENSE, category_name="Groceries & Food")
        self.tx_service.record_transaction(date="2026-09-06", amount=500.00, trans_type=TransactionType.EXPENSE, category_name="Groceries & Food", description="Massive spike")

        # Cash flow check
        cf = self.analytics_service.get_cashflow_summary("2026-09")
        self.assertEqual(cf.total_income, 3000.00)
        self.assertEqual(cf.total_expense, 700.00)
        self.assertEqual(cf.net_savings, 2300.00)

        # Statistics check
        stats = self.analytics_service.get_statistical_metrics("2026-09")
        self.assertEqual(stats["count"], 5)
        self.assertEqual(stats["min"], 50.00)
        self.assertEqual(stats["max"], 500.00)

        # Anomaly detection check (the 500 expense should trigger an outlier spike)
        anomalies = self.analytics_service.detect_spending_anomalies("2026-09", z_threshold=1.5)
        self.assertGreaterEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["amount"], 500.00)


if __name__ == "__main__":
    unittest.main()
