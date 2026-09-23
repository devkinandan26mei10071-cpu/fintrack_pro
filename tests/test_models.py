"""
Unit tests for domain models and data transfer objects.
"""

import unittest
from fintrack.models.domain import (
    Transaction,
    TransactionType,
    Category,
    Budget,
    BudgetStatus,
    AlertLevel,
    CashFlowSummary,
)


class TestDomainModels(unittest.TestCase):

    def test_transaction_type_enum(self):
        self.assertEqual(TransactionType.from_str("income"), TransactionType.INCOME)
        self.assertEqual(TransactionType.from_str("EXPENSE"), TransactionType.EXPENSE)
        self.assertEqual(TransactionType.from_str("inc"), TransactionType.INCOME)
        self.assertEqual(TransactionType.from_str("exp"), TransactionType.EXPENSE)

        with self.assertRaises(ValueError):
            TransactionType.from_str("INVALID")

    def test_category_model_dict(self):
        cat = Category(id=1, name="Groceries", type=TransactionType.EXPENSE, description="Food shopping")
        d = cat.to_dict()
        self.assertEqual(d["id"], 1)
        self.assertEqual(d["name"], "Groceries")
        self.assertEqual(d["type"], "EXPENSE")

    def test_transaction_model_dict(self):
        tx = Transaction(
            id=10,
            date="2026-09-15",
            amount=54.25,
            type=TransactionType.EXPENSE,
            category_id=2,
            category_name="Groceries",
            description="Supermarket run",
            payment_method="Debit Card"
        )
        d = tx.to_dict()
        self.assertEqual(d["amount"], 54.25)
        self.assertEqual(d["category_name"], "Groceries")
        self.assertEqual(d["type"], "EXPENSE")

    def test_budget_status_representation(self):
        status = BudgetStatus(
            category_id=1,
            category_name="Dining",
            month="2026-09",
            limit_amount=200.0,
            spent_amount=250.0,
            remaining_amount=-50.0,
            percentage_used=125.0,
            alert_level=AlertLevel.EXCEEDED
        )
        self.assertEqual(status.alert_level, AlertLevel.EXCEEDED)
        self.assertTrue(status.remaining_amount < 0)


if __name__ == "__main__":
    unittest.main()
