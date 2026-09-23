"""
SQLite database manager and schema initialization.
Enforces relational integrity, foreign key constraints, indexes for query performance, and default seeds.
"""

import os
from pathlib import Path
import sqlite3
from typing import Optional
from fintrack.utils.logger import app_logger


SCHEMA_SQL = """
-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK(type IN ('INCOME', 'EXPENSE')),
    description TEXT DEFAULT ''
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL CHECK(length(date) = 10),
    amount REAL NOT NULL CHECK(amount > 0),
    type TEXT NOT NULL CHECK(type IN ('INCOME', 'EXPENSE')),
    category_id INTEGER NOT NULL,
    description TEXT DEFAULT '',
    payment_method TEXT DEFAULT 'Cash',
    created_at TEXT NOT NULL,
    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- Budgets table
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    month TEXT NOT NULL CHECK(length(month) = 7),
    limit_amount REAL NOT NULL CHECK(limit_amount > 0),
    created_at TEXT NOT NULL,
    UNIQUE(category_id, month),
    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Audit logs table for security tracking
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    details TEXT
);

-- Performance Optimization Indexes
CREATE INDEX IF NOT EXISTS idx_trans_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_trans_category ON transactions(category_id);
CREATE INDEX IF NOT EXISTS idx_trans_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_budgets_month ON budgets(month);
"""

DEFAULT_CATEGORIES = [
    # Expenses
    ("Housing & Rent", "EXPENSE", "Apartment rent, home maintenance, mortgage"),
    ("Groceries & Food", "EXPENSE", "Supermarket food, household supplies"),
    ("Dining Out", "EXPENSE", "Restaurants, takeout, cafes"),
    ("Transportation", "EXPENSE", "Fuel, metro, public transport, cab rides"),
    ("Utilities & Bills", "EXPENSE", "Electricity, water, gas, internet, phone"),
    ("Healthcare & Fitness", "EXPENSE", "Pharmacy, medical consultations, gym"),
    ("Entertainment & Leisure", "EXPENSE", "Movies, streaming subscriptions, games"),
    ("Education & Books", "EXPENSE", "Courses, university fees, stationery, books"),
    ("Personal Care & Clothing", "EXPENSE", "Apparel, haircuts, cosmetics"),
    ("Miscellaneous Expense", "EXPENSE", "Unplanned incidental spending"),
    # Incomes
    ("Salary & Wages", "INCOME", "Primary monthly salary or contract pay"),
    ("Freelancing & Side Hustle", "INCOME", "Consulting, gig work, project payouts"),
    ("Investments & Dividends", "INCOME", "Stocks, mutual funds, interest payouts"),
    ("Scholarships & Grants", "INCOME", "Academic stipends, student assistance"),
    ("Gifts & Other Income", "INCOME", "Monetary gifts, cashback, refunds")
]


class Database:
    """Manages SQLite database lifecycle and schema provisioning."""

    def __init__(self, db_path: str = "data/fintrack.db"):
        self.db_path = db_path
        self._mem_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            self._mem_conn = sqlite3.connect(":memory:")
            self._mem_conn.row_factory = sqlite3.Row
            self._mem_conn.execute("PRAGMA foreign_keys = ON;")
        self._ensure_parent_directory()
        self.initialize_schema()

    def _ensure_parent_directory(self) -> None:
        """Creates the database directory if it does not exist (unless using in-memory :memory:)."""
        if self.db_path != ":memory:":
            path = Path(self.db_path)
            path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """
        Returns a configured sqlite3 connection with Row factory and enforced foreign keys.
        """
        if self._mem_conn is not None:
            return self._mem_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize_schema(self) -> None:
        """Creates tables, indexes, and default categories."""
        try:
            with self.get_connection() as conn:
                conn.executescript(SCHEMA_SQL)
                # Seed default categories if empty
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) AS count FROM categories;")
                count = cursor.fetchone()["count"]
                if count == 0:
                    cursor.executemany(
                        "INSERT INTO categories (name, type, description) VALUES (?, ?, ?);",
                        DEFAULT_CATEGORIES
                    )
                    app_logger.info(f"Seeded {len(DEFAULT_CATEGORIES)} default financial categories.")
            app_logger.info(f"Database schema initialized successfully at '{self.db_path}'.")
        except Exception as e:
            app_logger.error(f"Failed to initialize database schema: {e}")
            raise
