from datetime import datetime, date
from typing import Any, Dict

def serialize_datetime(obj: Any) -> Any:
    """JSON serialization için datetime helper"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    return obj

def format_currency(amount: float, currency: str = "TL") -> str:
    """Para formatı helper"""
    return f"{amount:,.2f} {currency}"

def calculate_percentage(part: float, total: float) -> float:
    """Yüzde hesaplama helper"""
    if total == 0:
        return 0.0
    return (part / total) * 100

def validate_expense_data(data: Dict) -> bool:
    """Harcama verisi validasyonu"""
    required_categories = ['food', 'transport', 'bills', 'entertainment', 'health', 'clothing']
    
    for category in required_categories:
        if category not in data:
            return False
        if not isinstance(data[category], (int, float)) or data[category] < 0:
            return False
    
    return True 