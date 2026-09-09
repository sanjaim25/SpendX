from datetime import datetime


def _parse_flexible_date(date_text: str) -> bool:
    """Return True when date_text matches a supported date format."""
    for fmt in ('%Y-%m-%d', '%d-%m-%Y'):
        try:
            datetime.strptime(date_text, fmt)
            return True
        except ValueError:
            continue
    return False


def validate_expense_input(data: dict) -> str | None:
    """Validate expense input. Returns error string or None."""
    if not data:
        return "Request body is empty"
    if 'description' not in data or not data['description'].strip():
        return "Description is required"
    if 'amount' not in data:
        return "Amount is required"
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return "Amount must be greater than 0"
    except (ValueError, TypeError):
        return "Amount must be a valid number"
    if 'date' in data and data['date']:
        if not _parse_flexible_date(data['date']):
            return "Date must be in YYYY-MM-DD or DD-MM-YYYY format"
    return None


def validate_user_input(data: dict) -> str | None:
    """Validate user registration input."""
    if not data:
        return "Request body is empty"
    if 'name' not in data or not data['name'].strip():
        return "Name is required"
    if 'email' not in data or not data['email'].strip():
        return "Email is required"
    if '@' not in data['email'] or '.' not in data['email']:
        return "Invalid email format"
    if 'password' not in data or len(data['password']) < 6:
        return "Password must be at least 6 characters"
    return None


def validate_budget_input(data: dict) -> str | None:
    """Validate budget input."""
    if not data:
        return "Request body is empty"
    if 'category' not in data or not data['category'].strip():
        return "Category is required"
    if 'monthly_limit' not in data:
        return "Monthly limit is required"
    try:
        limit = float(data['monthly_limit'])
        if limit <= 0:
            return "Monthly limit must be greater than 0"
    except (ValueError, TypeError):
        return "Monthly limit must be a valid number"
    return None
