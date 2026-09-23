"""
Unit tests for Database connection manager, schema initialization, and Repository DAO methods.
Utilizes isolated in-memory SQLite instances.
"""

import unittest
from fintrack.models.domain import Transaction, TransactionType, Category
from fintrack.storage.database import Database
from fintrack.storage.repository import FinanceRepository


class TestFinanceRepository(unittest.TestCase):

    def setUp(self):
        """Initializes a fresh in-memory database for each test run."""
        self.db = Database(db_path=":memory:")
        self.repo = FinanceRepository(self.db)

    def test_schema_and_default_categories(self):
        cats = self.repo.get_categories()
        self.assertGreaterEqual(len(cats), 10)
        expense_cats = self.repo.get_categories(TransactionType.EXPENSE)
        income_cats = self.repo.get_categories(TransactionType.INCOME)
        self.assertTrue(any(c.name == "Housing & Rent" for c in expense_cats))
        self.assertTrue(any(c.name == "Salary & Wages" for c in income_cats))

    def test_add_and_retrieve_category(self):
        new_cat = self.repo.add_category("Crypto Investments", TransactionType.INCOME, "Bitcoin & ETH")
        self.assertIsNotNone(new_cat.id)
        fetched = self.repo.get_category_by_id(new_cat.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, "Crypto Investments")

    def test_transaction_crud(self):
        cats = self.repo.get_categories(TransactionType.EXPENSE)
        test_cat = cats[0]

        # Create
        tx = Transaction(
            id=None,
            date="2026-09-20",
            amount=45.00,
            type=TransactionType.EXPENSE,
            category_id=test_cat.id,
            description="Quick test expense",
            payment_method="Cash"
        )
        saved = self.repo.add_transaction(tx)
        self.assertIsNotNone(saved.id)

        # Read
        retrieved = self.repo.get_transaction_by_id(saved.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.amount, 45.00)
        self.assertEqual(retrieved.category_name, test_cat.name)

        # Update
        retrieved.amount = 55.00
        retrieved.description = "Updated description"
        success = self.repo.update_transaction(retrieved)
        self.assertTrue(success)

        updated = self.repo.get_transaction_by_id(saved.id)
        self.assertEqual(updated.amount, 55.00)
        self.assertEqual(updated.description, "Updated description")

        # Delete
        del_success = self.repo.delete_transaction(saved.id)
        self.assertTrue(del_success)
        self.assertIsNone(self.repo.get_transaction_by_id(saved.id))

    def test_budget_upsert_and_fetch(self):
        cat = self.repo.get_category_by_name("Groceries & Food")
        self.assertIsNotNone(cat)

        # Insert budget
        b = self.repo.set_budget(cat.id, "2026-09", 400.0)
        self.assertEqual(b.limit_amount, 400.0)

        # Upsert (update existing)
        b_up = self.repo.set_budget(cat.id, "2026-09", 450.0)
        self.assertEqual(b_up.limit_amount, 450.0)

        budgets = self.repo.get_budgets_by_month("2026-09")
        self.assertEqual(len(budgets), 1)
        self.assertEqual(budgets[0].limit_amount, 450.0)

        # Delete
        del_b = self.repo.delete_budget(cat.id, "2026-09")
        self.assertTrue(del_b)
        self.assertEqual(len(self.repo.get_budgets_by_month("2026-09")), 0)


if __name__ == "__main__":
    unittest.main()
