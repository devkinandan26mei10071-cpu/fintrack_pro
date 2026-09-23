"""
Data Interchange & Portability Service.
Handles bidirectional synchronization, CSV/JSON bulk import, and formatted exports
with transactional integrity and schema validation.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple
from fintrack.models.domain import Transaction, TransactionType
from fintrack.services.transaction_service import TransactionService
from fintrack.utils.validators import ValidationError
from fintrack.utils.logger import app_logger


class ExportService:
    """Provides file export and import capabilities for CSV and JSON data interchange."""

    def __init__(self, tx_service: TransactionService):
        self.tx_service = tx_service

    def export_to_csv(self, file_path: str) -> int:
        """
        Exports all transactions to a structured CSV file.
        Returns the number of exported records.
        """
        transactions = self.tx_service.list_transactions(limit=100_000)
        target = Path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        with open(target, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Write Header
            writer.writerow(["ID", "Date", "Amount", "Type", "Category", "PaymentMethod", "Description"])
            for t in transactions:
                writer.writerow([
                    t.id,
                    t.date,
                    f"{t.amount:.2f}",
                    t.type.value,
                    t.category_name,
                    t.payment_method,
                    t.description
                ])

        app_logger.info(f"Exported {len(transactions)} transactions to CSV: {file_path}")
        return len(transactions)

    def export_to_json(self, file_path: str) -> int:
        """
        Exports all transactions and metadata into a formatted JSON structure.
        """
        transactions = self.tx_service.list_transactions(limit=100_000)
        target = Path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": "1.0.0",
            "total_records": len(transactions),
            "transactions": [t.to_dict() for t in transactions]
        }

        with open(target, mode="w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        app_logger.info(f"Exported {len(transactions)} transactions to JSON: {file_path}")
        return len(transactions)

    def import_from_csv(self, file_path: str) -> Tuple[int, List[str]]:
        """
        Imports transactions from a CSV file.
        Returns a tuple of (successful_count, error_messages).
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: '{file_path}'")

        success_count = 0
        errors: List[str] = []

        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValidationError("CSV file is empty or missing headers.")

            # Normalize headers
            header_map = {h.strip().lower(): h for h in reader.fieldnames}
            date_col = header_map.get("date")
            amt_col = header_map.get("amount")
            type_col = header_map.get("type")
            cat_col = header_map.get("category")
            desc_col = header_map.get("description", "")
            method_col = header_map.get("paymentmethod", "")

            if not (date_col and amt_col and type_col):
                raise ValidationError("CSV must contain 'Date', 'Amount', and 'Type' columns.")

            for line_no, row in enumerate(reader, start=2):
                try:
                    date_val = row[date_col].strip()
                    amt_val = float(row[amt_col].strip())
                    type_val = row[type_col].strip()
                    cat_val = row[cat_col].strip() if cat_col and row.get(cat_col) else None
                    desc_val = row[desc_col].strip() if desc_col and row.get(desc_col) else ""
                    method_val = row[method_col].strip() if method_col and row.get(method_col) else "Cash"

                    self.tx_service.record_transaction(
                        date=date_val,
                        amount=amt_val,
                        trans_type=type_val,
                        category_name=cat_val,
                        description=desc_val,
                        payment_method=method_val
                    )
                    success_count += 1
                except Exception as e:
                    errors.append(f"Row {line_no}: {str(e)}")

        app_logger.info(f"CSV Import completed: {success_count} succeeded, {len(errors)} failed.")
        return success_count, errors
