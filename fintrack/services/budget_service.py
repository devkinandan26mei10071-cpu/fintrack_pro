"""
Module 2: Budget & Alert Intelligence Service.
Monitors category spending thresholds, calculates budget variances,
and evaluates financial risk alerts (Safe, Warning, Exceeded).
"""

from typing import List, Optional, Dict
from fintrack.models.domain import Budget, BudgetStatus, AlertLevel, TransactionType
from fintrack.storage.repository import FinanceRepository
from fintrack.utils.validators import validate_amount, validate_month_year, ValidationError
from fintrack.utils.logger import app_logger


class BudgetService:
    """Manages monthly budgeting rules, spending limits, and automated warning triggers."""

    def __init__(self, repo: FinanceRepository):
        self.repo = repo

    def set_category_budget(self, category_id: int, month: str, limit_amount: float | str) -> Budget:
        """Sets or updates a spending cap for a specific category in a given month."""
        valid_month = validate_month_year(month)
        valid_limit = validate_amount(limit_amount)

        category = self.repo.get_category_by_id(category_id)
        if not category:
            raise ValidationError(f"Category ID {category_id} not found.")

        if category.type != TransactionType.EXPENSE:
            raise ValidationError(f"Budgets can only be set for EXPENSE categories. '{category.name}' is an {category.type.value} category.")

        budget = self.repo.set_budget(category_id, valid_month, valid_limit)
        app_logger.info(f"Budget configured: Category {category.name}, Month: {valid_month}, Limit: ${valid_limit:.2f}")
        return budget

    def get_budget_statuses(self, month: str) -> List[BudgetStatus]:
        """
        Calculates spending vs limit for all configured budgets in a month.
        Applies algorithmic threshold evaluation to classify AlertLevel.
        """
        valid_month = validate_month_year(month)
        budgets = self.repo.get_budgets_by_month(valid_month)

        # Get actual spending per category for this month
        spending_list = self.repo.get_monthly_spending_by_category(valid_month)
        spent_map: Dict[int, float] = {
            item["category_id"]: float(item["total_spent"])
            for item in spending_list
        }

        statuses: List[BudgetStatus] = []
        for b in budgets:
            cat_id = b.category_id
            spent = spent_map.get(cat_id, 0.0)
            limit = b.limit_amount
            remaining = limit - spent
            pct_used = (spent / limit * 100.0) if limit > 0 else 0.0

            # Determine alert level
            if pct_used >= 100.0:
                alert = AlertLevel.EXCEEDED
            elif pct_used >= 80.0:
                alert = AlertLevel.WARNING
            else:
                alert = AlertLevel.SAFE

            statuses.append(
                BudgetStatus(
                    category_id=cat_id,
                    category_name=b.category_name,
                    month=valid_month,
                    limit_amount=round(limit, 2),
                    spent_amount=round(spent, 2),
                    remaining_amount=round(remaining, 2),
                    percentage_used=round(pct_used, 1),
                    alert_level=alert
                )
            )

        # Sort: Exceeded first, then Warning, then Safe
        severity_order = {AlertLevel.EXCEEDED: 0, AlertLevel.WARNING: 1, AlertLevel.SAFE: 2}
        statuses.sort(key=lambda x: (severity_order[x.alert_level], -x.percentage_used))
        return statuses

    def remove_budget(self, category_id: int, month: str) -> bool:
        """Deletes a budget allowance."""
        valid_month = validate_month_year(month)
        return self.repo.delete_budget(category_id, valid_month)
