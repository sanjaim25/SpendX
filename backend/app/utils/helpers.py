from datetime import datetime, date


def format_currency(amount: float, symbol: str = '₹') -> str:
    """Format amount as Indian currency."""
    return f"{symbol}{amount:,.2f}"


def get_current_month_year() -> tuple:
    """Return current (month, year)."""
    now = datetime.now()
    return now.month, now.year


def month_name(month_number: int) -> str:
    """Convert month number to name."""
    months = [
        '', 'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    return months[month_number] if 1 <= month_number <= 12 else 'Unknown'


def date_range_filter(year: int, month: int) -> tuple:
    """Return start and end date for a month."""
    import calendar
    start = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end = date(year, month, last_day)
    return start, end


def parse_date(date_str: str) -> date:
    """Parse date string to date object."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return date.today()


def calculate_percentage(part: float, total: float) -> float:
    """Safe percentage calculation."""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)


def group_by_month(expenses: list) -> dict:
    """Group expenses by month."""
    grouped = {}
    for expense in expenses:
        key = f"{expense.date.year}-{str(expense.date.month).zfill(2)}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(expense)
    return dict(sorted(grouped.items()))
