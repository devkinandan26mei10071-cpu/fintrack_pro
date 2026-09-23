"""
Module 3: Financial Analytics & Statistical Intelligence Service.
Computes cash flow balance, category distributions, savings ratios,
moving averages, and statistical anomaly detection (outlier spending).
"""

from datetime import datetime
import math
from typing import List, Dict, Any, Optional
from fintrack.models.domain import CashFlowSummary, CategorySpend, TransactionType, Transaction
from fintrack.storage.repository import FinanceRepository
from fintrack.utils.validators import validate_month_year
from fintrack.utils.logger import app_logger


class AnalyticsService:
    """Provides statistical aggregations, trend analysis, and anomaly detection."""

    def __init__(self, repo: FinanceRepository):
        self.repo = repo

    def get_cashflow_summary(self, month: str) -> CashFlowSummary:
        """
        Calculates monthly macro-financial health indicators:
        Total Income, Total Expense, Net Savings, and Savings Rate percentage.
        """
        valid_month = validate_month_year(month)
        cashflow = self.repo.get_monthly_cashflow(valid_month)

        income = cashflow["total_income"]
        expense = cashflow["total_expense"]
        net = income - expense
        savings_rate = (net / income * 100.0) if income > 0 else 0.0

        return CashFlowSummary(
            month=valid_month,
            total_income=round(income, 2),
            total_expense=round(expense, 2),
            net_savings=round(net, 2),
            savings_rate=round(savings_rate, 1),
            transaction_count=int(cashflow["tx_count"])
        )

    def get_category_breakdown(self, month: str) -> List[CategorySpend]:
        """
        Computes expense category distribution and relative percentage contribution.
        """
        valid_month = validate_month_year(month)
        raw_items = self.repo.get_monthly_spending_by_category(valid_month)
        total_expense = sum(item["total_spent"] for item in raw_items)

        breakdown: List[CategorySpend] = []
        for item in raw_items:
            spent = float(item["total_spent"])
            pct = (spent / total_expense * 100.0) if total_expense > 0 else 0.0
            breakdown.append(
                CategorySpend(
                    category_name=item["category_name"],
                    total_amount=round(spent, 2),
                    percentage_of_total=round(pct, 1),
                    transaction_count=int(item["tx_count"])
                )
            )
        return breakdown

    def get_statistical_metrics(self, month: str) -> Dict[str, Any]:
        """
        Calculates descriptive statistics for expenses in the given month:
        Mean, median, standard deviation, and daily spending velocity.
        """
        valid_month = validate_month_year(month)
        start_date = f"{valid_month}-01"
        end_date = f"{valid_month}-31"

        transactions = self.repo.filter_transactions(
            start_date=start_date,
            end_date=end_date,
            trans_type=TransactionType.EXPENSE,
            limit=1000
        )

        if not transactions:
            return {
                "month": valid_month,
                "count": 0,
                "mean": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
                "min": 0.0,
                "max": 0.0,
                "daily_velocity": 0.0,
            }

        amounts = [t.amount for t in transactions]
        amounts.sort()
        n = len(amounts)
        total = sum(amounts)
        mean = total / n

        # Median
        if n % 2 == 1:
            median = amounts[n // 2]
        else:
            median = (amounts[(n // 2) - 1] + amounts[n // 2]) / 2.0

        # Sample Standard Deviation
        variance = sum((x - mean) ** 2 for x in amounts) / (n - 1) if n > 1 else 0.0
        std_dev = math.sqrt(variance)

        # Daily spending velocity (assuming standard 30-day month approximation)
        daily_velocity = total / 30.0

        return {
            "month": valid_month,
            "count": n,
            "mean": round(mean, 2),
            "median": round(median, 2),
            "std_dev": round(std_dev, 2),
            "min": round(amounts[0], 2),
            "max": round(amounts[-1], 2),
            "daily_velocity": round(daily_velocity, 2),
        }

    def detect_spending_anomalies(self, month: str, z_threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        Algorithm: Z-Score Statistical Anomaly Detection.
        Flags transactions whose cost exceeds the mean by more than `z_threshold` standard deviations.
        """
        valid_month = validate_month_year(month)
        start_date = f"{valid_month}-01"
        end_date = f"{valid_month}-31"

        transactions = self.repo.filter_transactions(
            start_date=start_date,
            end_date=end_date,
            trans_type=TransactionType.EXPENSE,
            limit=1000
        )

        if len(transactions) < 5:
            # Need adequate sample size for meaningful statistical anomaly detection
            return []

        amounts = [t.amount for t in transactions]
        mean = sum(amounts) / len(amounts)
        std_dev = math.sqrt(sum((x - mean) ** 2 for x in amounts) / (len(amounts) - 1))

        if std_dev == 0:
            return []

        anomalies: List[Dict[str, Any]] = []
        for t in transactions:
            z_score = (t.amount - mean) / std_dev
            if z_score >= z_threshold:
                anomalies.append({
                    "id": t.id,
                    "date": t.date,
                    "category": t.category_name,
                    "amount": t.amount,
                    "description": t.description,
                    "z_score": round(z_score, 2),
                    "deviation_over_mean": round(t.amount - mean, 2)
                })

        return sorted(anomalies, key=lambda x: x["z_score"], reverse=True)
