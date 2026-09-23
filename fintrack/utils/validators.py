"""
Input validators and sanitizers for financial data processing.
Ensures strong typing, bounds checking, regex validation, and security sanitization.
"""

from datetime import datetime
import re
from typing import Optional, Tuple


class ValidationError(ValueError):
    """Custom exception raised when financial data fails business validation."""
    pass


def validate_amount(amount_input: str | float | int, min_val: float = 0.01, max_val: float = 100_000_000.0) -> float:
    """
    Validates and converts a monetary amount.
    
    Args:
        amount_input: String or numeric representation of monetary amount.
        min_val: Minimum acceptable amount (default: 0.01).
        max_val: Maximum acceptable transaction amount.
        
    Returns:
        Rounded float value (2 decimal places).
        
    Raises:
        ValidationError: If invalid format or out of bounds.
    """
    try:
        val = float(amount_input)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid monetary amount: '{amount_input}'. Must be a valid positive number.")

    if val < min_val:
        raise ValidationError(f"Amount must be at least {min_val:.2f}. Received: {val:.2f}")
    if val > max_val:
        raise ValidationError(f"Amount exceeds maximum threshold of {max_val:,.2f}. Received: {val:,.2f}")

    return round(val, 2)


def validate_date(date_str: str) -> str:
    """
    Validates that a date string follows the ISO standard 'YYYY-MM-DD' and is a real calendar date.
    
    Args:
        date_str: Date string in 'YYYY-MM-DD' format.
        
    Returns:
        Canonical date string 'YYYY-MM-DD'.
        
    Raises:
        ValidationError: If date does not match format or is invalid calendar day.
    """
    if not isinstance(date_str, str):
        raise ValidationError("Date must be a string in YYYY-MM-DD format.")

    date_str = date_str.strip()
    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", date_str)
    if not match:
        raise ValidationError(f"Invalid date format '{date_str}'. Expected format is YYYY-MM-DD.")

    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        if parsed.year < 2000 or parsed.year > 2099:
            raise ValidationError(f"Year {parsed.year} is out of allowable range (2000-2099).")
        return parsed.strftime("%Y-%m-%d")
    except ValueError as e:
        raise ValidationError(f"Invalid calendar date '{date_str}': {str(e)}")


def validate_category_name(name: str) -> str:
    """
    Validates and sanitizes a category name.
    
    Args:
        name: Name of category.
        
    Returns:
        Cleaned category name.
        
    Raises:
        ValidationError: If name is empty, too long, or contains disallowed special characters.
    """
    if not name or not isinstance(name, str):
        raise ValidationError("Category name cannot be empty.")

    cleaned = name.strip()
    if len(cleaned) < 2 or len(cleaned) > 50:
        raise ValidationError("Category name must be between 2 and 50 characters.")

    if not re.match(r"^[A-Za-z0-9\s\-_&/]+$", cleaned):
        raise ValidationError("Category name contains disallowed characters. Use letters, numbers, spaces, and -_&/ only.")

    return cleaned


def validate_description(description: Optional[str]) -> str:
    """
    Sanitizes transaction description and strips control characters.
    """
    if not description:
        return ""
    cleaned = description.strip()
    if len(cleaned) > 255:
        raise ValidationError("Description cannot exceed 255 characters.")
    # Prevent control characters
    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", cleaned)
    return cleaned


def validate_month_year(month_str: str) -> str:
    """
    Validates 'YYYY-MM' format for monthly budget and reporting.
    """
    if not isinstance(month_str, str):
        raise ValidationError("Month string must be formatted as YYYY-MM.")
    cleaned = month_str.strip()
    match = re.match(r"^(\d{4})-(\d{2})$", cleaned)
    if not match:
        raise ValidationError(f"Invalid month format '{cleaned}'. Expected format: YYYY-MM (e.g. 2026-09).")
    year, month = int(match.group(1)), int(match.group(2))
    if month < 1 or month > 12:
        raise ValidationError(f"Month must be between 01 and 12. Got: {month:02d}")
    return f"{year:04d}-{month:02d}"
