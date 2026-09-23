"""
Data Access Object (DAO) repository implementing persistence operations for FinTrack Pro.
Encapsulates all SQL queries, parameterization, and transaction rollback semantics.
"""

from datetime import datetime
import sqlite3
from typing import List, Optional, Tuple, Dict, Any

from fintrack.models.domain import (
    Transaction,
    TransactionType,
    Category,
    Budget,
    AuditLog,
)
from fintrack.storage.database import Database
from fintrack.utils.logger import app_logger


class FinanceRepository:
    """Provides abstracted data access methods with full parameterized security."""

    def __init__(self, db: Database):
        self.db = db

    # ==========================================
    # AUDIT LOGGING
    # ==========================================
    def _log_audit_with_conn(self, conn: sqlite3.Connection, action: str, entity_type: str, entity_id: Optional[int], details: str) -> None:
        """Records an audit event using the active transactional connection."""
        timestamp = datetime.now().isoformat()
        try:
            conn.execute(
                "INSERT INTO audit_logs (timestamp, action, entity_type, entity_id, details) VALUES (?, ?, ?, ?, ?);",
                (timestamp, action, entity_type, entity_id, details)
            )
        except Exception as e:
            app_logger.warning(f"Could not record audit log: {e}")

    def log_audit(self, action: str, entity_type: str, entity_id: Optional[int], details: str) -> None:
        """Records an administrative or data mutation event into the audit trail."""
        timestamp = datetime.now().isoformat()
        try:
            with self.db.get_connection() as conn:
                self._log_audit_with_conn(conn, action, entity_type, entity_id, details)
        except Exception as e:
            app_logger.warning(f"Could not record audit log: {e}")

    # ==========================================
    # CATEGORIES
    # ==========================================
    def get_categories(self, trans_type: Optional[TransactionType] = None) -> List[Category]:
        """Fetches all categories, optionally filtered by income or expense."""
        query = "SELECT id, name, type, description FROM categories"
        params: Tuple[Any, ...] = ()
        if trans_type:
            query += " WHERE type = ?"
            params = (trans_type.value,)
        query += " ORDER BY name ASC;"

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                Category(
                    id=row["id"],
                    name=row["name"],
                    type=TransactionType(row["type"]),
                    description=row["description"] or ""
                )
                for row in rows
            ]

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Retrieves a single category by primary key."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, type, description FROM categories WHERE id = ?;", (category_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Category(
                id=row["id"],
                name=row["name"],
                type=TransactionType(row["type"]),
                description=row["description"] or ""
            )

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Case-insensitive search for a category by name."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, type, description FROM categories WHERE LOWER(name) = LOWER(?);", (name.strip(),))
            row = cursor.fetchone()
            if not row:
                return None
            return Category(
                id=row["id"],
                name=row["name"],
                type=TransactionType(row["type"]),
                description=row["description"] or ""
            )

    def add_category(self, name: str, cat_type: TransactionType, description: str = "") -> Category:
        """Inserts a new user-defined category."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO categories (name, type, description) VALUES (?, ?, ?);",
                (name.strip(), cat_type.value, description.strip())
            )
            cat_id = cursor.lastrowid
            self._log_audit_with_conn(conn, "CREATE", "Category", cat_id, f"Added category '{name}' ({cat_type.value})")
            return Category(id=cat_id, name=name.strip(), type=cat_type, description=description.strip())

    # ==========================================
    # TRANSACTIONS
    # ==========================================
    def add_transaction(self, tx: Transaction) -> Transaction:
        """Persists a new monetary transaction."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO transactions (date, amount, type, category_id, description, payment_method, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (tx.date, tx.amount, tx.type.value, tx.category_id, tx.description, tx.payment_method, tx.created_at)
            )
            tx.id = cursor.lastrowid
            self._log_audit_with_conn(conn, "CREATE", "Transaction", tx.id, f"{tx.type.value} of ${tx.amount:.2f} on {tx.date}")
            return tx

    def get_transaction_by_id(self, tx_id: int) -> Optional[Transaction]:
        """Fetches a transaction joined with category name."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT t.id, t.date, t.amount, t.type, t.category_id, c.name AS category_name,
                       t.description, t.payment_method, t.created_at
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.id = ?;
                """,
                (tx_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return Transaction(
                id=row["id"],
                date=row["date"],
                amount=row["amount"],
                type=TransactionType(row["type"]),
                category_id=row["category_id"],
                category_name=row["category_name"],
                description=row["description"],
                payment_method=row["payment_method"],
                created_at=row["created_at"]
            )

    def delete_transaction(self, tx_id: int) -> bool:
        """Deletes a transaction by ID."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?;", (tx_id,))
            deleted = cursor.rowcount > 0
            if deleted:
                self._log_audit_with_conn(conn, "DELETE", "Transaction", tx_id, f"Deleted transaction {tx_id}")
            return deleted

    def update_transaction(self, tx: Transaction) -> bool:
        """Updates fields of an existing transaction."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE transactions
                SET date = ?, amount = ?, type = ?, category_id = ?, description = ?, payment_method = ?
                WHERE id = ?;
                """,
                (tx.date, tx.amount, tx.type.value, tx.category_id, tx.description, tx.payment_method, tx.id)
            )
            updated = cursor.rowcount > 0
            if updated:
                self._log_audit_with_conn(conn, "UPDATE", "Transaction", tx.id, f"Updated transaction {tx.id}")
            return updated

    def filter_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        trans_type: Optional[TransactionType] = None,
        category_id: Optional[int] = None,
        search_query: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Transaction]:
        """
        Versatile parameterized query with multiple filter criteria.
        """
        conditions = []
        params: List[Any] = []

        if start_date:
            conditions.append("t.date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("t.date <= ?")
            params.append(end_date)
        if trans_type:
            conditions.append("t.type = ?")
            params.append(trans_type.value)
        if category_id:
            conditions.append("t.category_id = ?")
            params.append(category_id)
        if min_amount is not None:
            conditions.append("t.amount >= ?")
            params.append(min_amount)
        if max_amount is not None:
            conditions.append("t.amount <= ?")
            params.append(max_amount)
        if search_query:
            conditions.append("(t.description LIKE ? OR c.name LIKE ?)")
            search_param = f"%{search_query.strip()}%"
            params.extend([search_param, search_param])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
            SELECT t.id, t.date, t.amount, t.type, t.category_id, c.name AS category_name,
                   t.description, t.payment_method, t.created_at
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            {where_clause}
            ORDER BY t.date DESC, t.id DESC
            LIMIT ? OFFSET ?;
        """
        params.extend([limit, offset])

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                Transaction(
                    id=row["id"],
                    date=row["date"],
                    amount=row["amount"],
                    type=TransactionType(row["type"]),
                    category_id=row["category_id"],
                    category_name=row["category_name"],
                    description=row["description"],
                    payment_method=row["payment_method"],
                    created_at=row["created_at"]
                )
                for row in rows
            ]

    # ==========================================
    # BUDGETS
    # ==========================================
    def set_budget(self, category_id: int, month: str, limit_amount: float) -> Budget:
        """Creates or updates a monthly budget cap (UPSERT semantic)."""
        now = datetime.now().isoformat()
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO budgets (category_id, month, limit_amount, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(category_id, month) DO UPDATE SET limit_amount = excluded.limit_amount;
                """,
                (category_id, month, limit_amount, now)
            )
            self._log_audit_with_conn(conn, "UPSERT", "Budget", category_id, f"Budget for category {category_id} ({month}) set to ${limit_amount:.2f}")

        # Retrieve category name
        cat = self.get_category_by_id(category_id)
        cat_name = cat.name if cat else "Unknown"
        return Budget(id=None, category_id=category_id, category_name=cat_name, month=month, limit_amount=limit_amount)

    def get_budgets_by_month(self, month: str) -> List[Budget]:
        """Retrieves all budget limits established for a specific month."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT b.id, b.category_id, c.name AS category_name, b.month, b.limit_amount, b.created_at
                FROM budgets b
                JOIN categories c ON b.category_id = c.id
                WHERE b.month = ?
                ORDER BY c.name ASC;
                """,
                (month,)
            )
            rows = cursor.fetchall()
            return [
                Budget(
                    id=row["id"],
                    category_id=row["category_id"],
                    category_name=row["category_name"],
                    month=row["month"],
                    limit_amount=row["limit_amount"],
                    created_at=row["created_at"]
                )
                for row in rows
            ]

    def delete_budget(self, category_id: int, month: str) -> bool:
        """Deletes a budget allowance for a category in a month."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM budgets WHERE category_id = ? AND month = ?;", (category_id, month))
            deleted = cursor.rowcount > 0
            if deleted:
                self._log_audit_with_conn(conn, "DELETE", "Budget", category_id, f"Removed budget for {month}")
            return deleted

    # ==========================================
    # AGGREGATIONS FOR ANALYTICS
    # ==========================================
    def get_monthly_spending_by_category(self, month: str) -> List[Dict[str, Any]]:
        """Calculates total spend per expense category for a given month (YYYY-MM)."""
        start_date = f"{month}-01"
        end_date = f"{month}-31"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT c.id AS category_id, c.name AS category_name,
                       COALESCE(SUM(t.amount), 0.0) AS total_spent,
                       COUNT(t.id) AS tx_count
                FROM categories c
                LEFT JOIN transactions t ON c.id = t.category_id
                     AND t.type = 'EXPENSE'
                     AND t.date >= ? AND t.date <= ?
                WHERE c.type = 'EXPENSE'
                GROUP BY c.id, c.name
                HAVING total_spent > 0
                ORDER BY total_spent DESC;
                """,
                (start_date, end_date)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_monthly_cashflow(self, month: str) -> Dict[str, float]:
        """Calculates total income and total expense for a month."""
        start_date = f"{month}-01"
        end_date = f"{month}-31"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(CASE WHEN type = 'INCOME' THEN amount ELSE 0 END), 0.0) AS total_income,
                    COALESCE(SUM(CASE WHEN type = 'EXPENSE' THEN amount ELSE 0 END), 0.0) AS total_expense,
                    COUNT(id) AS tx_count
                FROM transactions
                WHERE date >= ? AND date <= ?;
                """,
                (start_date, end_date)
            )
            row = cursor.fetchone()
            return {
                "total_income": row["total_income"],
                "total_expense": row["total_expense"],
                "tx_count": row["tx_count"]
            }
