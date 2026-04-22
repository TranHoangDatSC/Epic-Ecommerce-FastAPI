"""
Utility functions for the application
"""

import os
import secrets
import string
from typing import Optional
from datetime import datetime


def generate_random_token(length: int = 32) -> str:
    """Generate a random token for email verification, password reset, etc."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_unique_key(base_string: str, length: int = 64) -> str:
    """Generate a unique key (random_key) for user"""
    random_part = secrets.token_hex(length // 2)
    return random_part


def format_price(price: float) -> str:
    """Format price for display"""
    return f"{price:,.2f}"


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime for display"""
    if dt is None:
        return ""
    return dt.strftime(format_str)


def get_order_status_text(status_code: int) -> str:
    """Get human-readable order status"""
    statuses = {
        0: "Pending",
        1: "Confirmed",
        2: "Shipping",
        3: "Delivered",
        4: "Cancelled"
    }
    return statuses.get(status_code, "Unknown")


def get_product_status_text(status_code: int) -> str:
    """Get human-readable product status"""
    statuses = {
        0: "Pending for Review",
        1: "Approved",
        2: "Rejected",
        3: "Sold Out"
    }
    return statuses.get(status_code, "Unknown")


def get_role_name(role_id: int) -> str:
    """Get role name from role ID"""
    roles = {
        1: "Admin",
        2: "Moderator",
        3: "User"
    }
    return roles.get(role_id, "Unknown")


def validate_email_format(email: str) -> bool:
    """Basic email format validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone_format(phone: str) -> bool:
    """Validate Vietnamese phone number format"""
    import re
    # Vietnamese phone: 0xxx xxx xxxx or +84xx xxxx xxxx
    pattern = r'^(?:\+?84|0)[0-9]{9,10}$'
    return re.match(pattern, phone) is not None


def truncate_string(text: Optional[str], length: int = 100, suffix: str = "...") -> str:
    """Truncate string to specified length"""
    if text is None:
        return ""
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix


def calculate_discount(original_price: float, discount_type: int, discount_value: float) -> float:
    """
    Calculate discounted price
    
    Args:
        original_price: Original price
        discount_type: 0 = Fixed amount, 1 = Percentage
        discount_value: Discount amount or percentage
    
    Returns:
        Discount amount
    """
    if discount_type == 0:  # Fixed amount
        return min(discount_value, original_price)
    elif discount_type == 1:  # Percentage
        return (original_price * discount_value) / 100
    return 0.0


def paginate(total: int, skip: int, limit: int) -> dict:
    """Calculate pagination info"""
    pages = (total + limit - 1) // limit  # Ceiling division
    current_page = (skip // limit) + 1
    
    return {
        "total": total,
        "pages": pages,
        "current_page": current_page,
        "skip": skip,
        "limit": limit,
        "has_next": current_page < pages,
        "has_previous": current_page > 1
    }
