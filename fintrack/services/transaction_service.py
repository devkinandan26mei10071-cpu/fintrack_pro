"""
Module 1: Transaction & Ledger Management Service.
Handles ledger operations, input sanitization, category verification,
and intelligent keyword-based auto-categorization algorithms.
"""

from typing import List, Optional, Tuple, Dict
from fintrack.models.domain import Transaction, TransactionType, Category
from fintrack.storage.repository import FinanceRepository
from fintrack.utils.validators import (
    validate_amount,
    validate_date,
    validate_category_name,
    validate_description,
    ValidationError,
)
from fintrack.utils.logger import app_logger


# Heuristic rule table for automatic keyword categorizer
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Housing & Rent": ["rent", "landlord", "apartment", "maintenance", "mortgage", "hoa"],
    "Groceries & Food": ["supermarket", "walmart", "grocery", "produce", "milk", "bread", "safeway", "trader"],
    "Dining Out": ["starbucks", "cafe", "restaurant", "burger", "pizza", "chipotle", "subway", "dinner", "lunch"],
    "Transportation": ["uber", "lyft", "metro", "bus", "fuel", "gas", "petrol", "parking", "toll", "subway"],
    "Utilities & Bills": ["electric", "water", "internet", "wifi", "bill", "power", "utility", "phone", "verizon"],
    "Healthcare & Fitness": ["doctor", "pharmacy", "medicine", "gym", "hospital", "clinic", "dental"],
    "Entertainment & Leisure": ["netflix", "spotify", "cinema", "movie", "steam", "game", "concert"],
    "Education & Books": ["tuition", "course", "udemy", "book", "university", "textbook", "college"],
    "Personal Care & Clothing": ["salon", "haircut", "apparel", "zara", "h&m", "clothing", "shoes"],
    "Salary & Wages": ["paycheck", "payroll", "salary", "wages", "employer", "direct deposit"],
    "Freelancing & Side Hustle": ["freelance", "upwork", "fiverr", "client", "consulting", "gig"],
    "Investments & Dividends": ["dividend", "interest", "stock", "vanguard", "fidelity", "etf", "crypto"],
}


class TransactionService:
    """Core business logic for recording and managing income & expense transactions."""

    def __init__(self, repo: FinanceRepository):
        self.repo = repo

    def auto_detect_category(self, description: str, trans_type: TransactionType) -> Optional[Category]:
        """
        Algorithm: Keyword-based matching algorithm to suggest or assign a category based on description text.
        Demonstrates pattern matching and string search in Python.
        """
        if not description:
            return None

        desc_lower = description.lower()
        for cat_name, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in desc_lower:
                    cat = self.repo.get_category_by_name(cat_name)
                    if cat and cat.type == trans_type:
                        return cat
        return None

    def record_transaction(
        self,
        date: str,
        amount: float | str,
        trans_type: TransactionType | str,
        category_id: Optional[int] = None,
        category_name: Optional[str] = None,
        description: str = "",
        payment_method: str = "Cash"
    ) -> Transaction:
        """
        Validates, prepares, and persists a financial transaction.
        """
        # Validate inputs
        valid_date = validate_date(date)
        valid_amount = validate_amount(amount)
        valid_desc = validate_description(description)
        payment_method = payment_method.strip() or "Cash"

        if isinstance(trans_type, str):
            trans_type = TransactionType.from_str(trans_type)

        # Resolve category
        category: Optional[Category] = None
        if category_id:
            category = self.repo.get_category_by_id(category_id)
            if not category:
                raise ValidationError(f"Category with ID {category_id} does not exist.")
        elif category_name:
            category = self.repo.get_category_by_name(category_name)
            if not category:
                raise ValidationError(f"Category '{category_name}' not found.")
        else:
            # Attempt auto-detection
            category = self.auto_detect_category(valid_desc, trans_type)
            if not category:
                # Default to fallback category
                default_name = "Salary & Wages" if trans_type == TransactionType.INCOME else "Miscellaneous Expense"
                category = self.repo.get_category_by_name(default_name)
                if not category:
                    cats = self.repo.get_categories(trans_type)
                    if cats:
                        category = cats[0]

        if not category:
            raise ValidationError("No matching category could be assigned. Please create or specify a category.")

        if category.type != trans_type:
            raise ValidationError(
                f"Category '{category.name}' has type {category.type.value}, which does not match transaction type {trans_type.value}."
            )

        tx = Transaction(
            id=None,
            date=valid_date,
            amount=valid_amount,
            type=trans_type,
            category_id=category.id, # type: ignore
            category_name=category.name,
            description=valid_desc,
            payment_method=payment_method
        )

        saved = self.repo.add_transaction(tx)
        app_logger.info(f"Transaction recorded successfully: ID {saved.id}, Amount: {saved.amount}")
        return saved

    def get_transaction(self, tx_id: int) -> Optional[Transaction]:
        """Fetches a transaction by ID."""
        return self.repo.get_transaction_by_id(tx_id)

    def remove_transaction(self, tx_id: int) -> bool:
        """Deletes a transaction."""
        return self.repo.delete_transaction(tx_id)

    def modify_transaction(
        self,
        tx_id: int,
        date: Optional[str] = None,
        amount: Optional[float | str] = None,
        trans_type: Optional[TransactionType | str] = None,
        category_id: Optional[int] = None,
        description: Optional[str] = None,
        payment_method: Optional[str] = None
    ) -> Transaction:
        """Updates attributes of an existing transaction."""
        existing = self.repo.get_transaction_by_id(tx_id)
        if not existing:
            raise ValidationError(f"Transaction {tx_id} does not exist.")

        if date is not None:
            existing.date = validate_date(date)
        if amount is not None:
            existing.amount = validate_amount(amount)
        if trans_type is not None:
            if isinstance(trans_type, str):
                trans_type = TransactionType.from_str(trans_type)
            existing.type = trans_type
        if description is not None:
            existing.description = validate_description(description)
        if payment_method is not None:
            existing.payment_method = payment_method.strip() or "Cash"

        if category_id is not None:
            cat = self.repo.get_category_by_id(category_id)
            if not cat:
                raise ValidationError(f"Category with ID {category_id} does not exist.")
            if cat.type != existing.type:
                raise ValidationError(f"Category {cat.name} type mismatch with transaction {existing.type.value}.")
            existing.category_id = cat.id # type: ignore
            existing.category_name = cat.name

        self.repo.update_transaction(existing)
        return existing

    def list_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        trans_type: Optional[TransactionType | str] = None,
        category_id: Optional[int] = None,
        search_query: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Transaction]:
        """Filters and retrieves transactions."""
        type_enum = None
        if trans_type:
            type_enum = TransactionType.from_str(trans_type) if isinstance(trans_type, str) else trans_type

        return self.repo.filter_transactions(
            start_date=start_date,
            end_date=end_date,
            trans_type=type_enum,
            category_id=category_id,
            search_query=search_query,
            min_amount=min_amount,
            max_amount=max_amount,
            limit=limit,
            offset=offset
        )

    def list_categories(self, trans_type: Optional[TransactionType | str] = None) -> List[Category]:
        """Lists categories, optionally filtered by type."""
        type_enum = None
        if trans_type:
            type_enum = TransactionType.from_str(trans_type) if isinstance(trans_type, str) else trans_type
        return self.repo.get_categories(type_enum)

    def create_category(self, name: str, cat_type: TransactionType | str, description: str = "") -> Category:
        """Creates a custom category with name validation."""
        valid_name = validate_category_name(name)
        type_enum = TransactionType.from_str(cat_type) if isinstance(cat_type, str) else cat_type
        existing = self.repo.get_category_by_name(valid_name)
        if existing:
            raise ValidationError(f"Category '{valid_name}' already exists.")
        return self.repo.add_category(valid_name, type_enum, description)
