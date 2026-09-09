from app.models import Expense
from app.ml_models.linear_regression_model import forecast_next_month, forecast_category_wise
from app import db
from datetime import datetime
from collections import defaultdict


def get_monthly_totals(user_id: int) -> list:
    """Build monthly totals from expense history."""
    expenses = Expense.query.filter_by(user_id=user_id).all()

    monthly_map = defaultdict(float)
    for expense in expenses:
        key = (expense.date.year, expense.date.month)
        monthly_map[key] += expense.amount

    sorted_months = sorted(monthly_map.keys())
    monthly_totals = [(i + 1, monthly_map[k]) for i, k in enumerate(sorted_months)]

    return monthly_totals


def get_category_monthly_data(user_id: int) -> dict:
    """Build category-wise monthly totals."""
    expenses = Expense.query.filter_by(user_id=user_id).all()

    category_map = defaultdict(lambda: defaultdict(float))
    for expense in expenses:
        key = (expense.date.year, expense.date.month)
        cat = expense.predicted_category or 'Uncategorized'
        category_map[cat][key] += expense.amount

    result = {}
    for cat, month_data in category_map.items():
        sorted_months = sorted(month_data.keys())
        result[cat] = [(i + 1, month_data[k]) for i, k in enumerate(sorted_months)]

    return result


def forecast_spending(user_id: int) -> dict:
    """Full forecast: total + category-wise."""
    monthly_totals = get_monthly_totals(user_id)

    if not monthly_totals:
        return {
            'status': 'no_data',
            'message': 'No expense data found. Add expenses to get forecasts.',
            'predicted_total': 0,
            'category_forecasts': {}
        }

    total_forecast = forecast_next_month(monthly_totals)

    category_monthly = get_category_monthly_data(user_id)
    category_forecasts = forecast_category_wise(category_monthly)

    current = datetime.now()
    next_month = current.month % 12 + 1
    next_year = current.year + (1 if current.month == 12 else 0)

    return {
        'status': 'success',
        'predicted_total': total_forecast['predicted_amount'],
        'trend': total_forecast['trend'],
        'trend_slope': total_forecast.get('slope', 0),
        'r_squared': total_forecast.get('r_squared', 0),
        'message': total_forecast['message'],
        'category_forecasts': {k: round(v, 2) for k, v in category_forecasts.items()},
        'months_analyzed': total_forecast.get('months_analyzed', 0),
        'forecast_for': f"{next_month}/{next_year}"
    }
