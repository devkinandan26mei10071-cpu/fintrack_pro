"""
Core domain models representing financial concepts, budgets, categories, and audit events.
Utilizes Python dataclasses and enums for strong typing and immutability guarantees where appropriate.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TransactionType(str, Enum):
    """Enumeration of permitted transaction types."""
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

    @classmethod
    def from_str(cls, value: str) -> "TransactionType":
        cleaned = value.strip().upper()
        if cleaned in ("INCOME", "INC", "+"):
            return cls.INCOME
        if cleaned in ("EXPENSE", "EXP", "-"):
            return cls.EXPENSE
        raise ValueError(f"Unknown transaction type: '{value}'. Expected INCOME or EXPENSE.")


class AlertLevel(str, Enum):
    """Alert thresholds for budget adherence."""
    SAFE = "SAFE"        # < 80%
    WARNING = "WARNING"  # 80% to 99%
    EXCEEDED = "EXCEEDED"# >= 100%


@dataclass
class Category:
    """Represents a budget or transaction category."""
    id: Optional[int]
    name: str
    type: TransactionType
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
        }


@dataclass
class Transaction:
    """Represents a single monetary income or expense transaction."""
    id: Optional[int]
    date: str  # YYYY-MM-DD
    amount: float
    type: TransactionType
    category_id: int
    category_name: str = ""
    description: str = ""
    payment_method: str = "Cash"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date,
            "amount": self.amount,
            "type": self.type.value,
            "category_id": self.category_id,
            "category_name": self.category_name,
            "description": self.description,
            "payment_method": self.payment_method,
            "created_at": self.created_at,
        }


@dataclass
class Budget:
    """Monthly spending allowance for an expense category."""
    id: Optional[int]
    category_id: int
    category_name: str
    month: str  # YYYY-MM
    limit_amount: float
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category_id": self.category_id,
            "category_name": self.category_name,
            "month": self.month,
            "limit_amount": self.limit_amount,
            "created_at": self.created_at,
        }


@dataclass
class BudgetStatus:
    """Calculated adherence state for a monthly budget."""
    category_id: int
    category_name: str
    month: str
    limit_amount: float
    spent_amount: float
    remaining_amount: float
    percentage_used: float
    alert_level: AlertLevel


@dataclass
class CashFlowSummary:
    """Monthly macroeconomic view of personal cash flow."""
    month: str
    total_income: float
    total_expense: float
    net_savings: float
    savings_rate: float
    transaction_count: int


@dataclass
class CategorySpend:
    """Spending breakdown by category for analytics and charts."""
    category_name: str
    total_amount: float
    percentage_of_total: float
    transaction_count: int


@dataclass
class AuditLog:
    """Security and compliance audit trail entry."""
    id: Optional[int]
    timestamp: str
    action: str
    entity_type: str
    entity_id: Optional[int]
    details: str
