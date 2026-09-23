"""
Unit tests for data export and import service (CSV & JSON).
"""

import os
import tempfile
import unittest
from pathlib import Path

from fintrack.models.domain import TransactionType
from fintrack.storage.database import Database
from fintrack.storage.repository import FinanceRepository
from fintrack.services.transaction_service import TransactionService
from fintrack.services.export_service import ExportService


class TestExportService(unittest.TestCase):

    def setUp(self):
        self.db = Database(db_path=":memory:")
        self.repo = FinanceRepository(self.db)
        self.tx_service = TransactionService(self.repo)
        self.export_service = ExportService(self.tx_service)

        # Seed 3 records
        self.tx_service.record_transaction("2026-09-01", 3000.0, TransactionType.INCOME, category_name="Salary & Wages")
        self.tx_service.record_transaction("2026-09-02", 75.0, TransactionType.EXPENSE, category_name="Groceries & Food", description="Weekly groceries")
        self.tx_service.record_transaction("2026-09-03", 25.0, TransactionType.EXPENSE, category_name="Transportation", description="Metro ticket")

        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_csv_export_and_reimport(self):
        csv_file = Path(self.temp_dir.name) / "test_out.csv"
        count = self.export_service.export_to_csv(str(csv_file))
        self.assertEqual(count, 3)
        self.assertTrue(csv_file.exists())

        # Test importing into a fresh database instance
        new_db = Database(db_path=":memory:")
        new_repo = FinanceRepository(new_db)
        new_tx_service = TransactionService(new_repo)
        new_export_service = ExportService(new_tx_service)

        imported_count, errors = new_export_service.import_from_csv(str(csv_file))
        self.assertEqual(imported_count, 3)
        self.assertEqual(len(errors), 0)

        # Verify records inside fresh database
        imported_list = new_tx_service.list_transactions()
        self.assertEqual(len(imported_list), 3)

    def test_json_export(self):
        json_file = Path(self.temp_dir.name) / "test_out.json"
        count = self.export_service.export_to_json(str(json_file))
        self.assertEqual(count, 3)
        self.assertTrue(json_file.exists())

        # Check content
        with open(json_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn('"total_records": 3', content)
            self.assertIn('"Salary & Wages"', content)


if __name__ == "__main__":
    unittest.main()
