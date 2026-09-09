from collections import defaultdict
from datetime import datetime

from app import db
from app.models import Budget, Expense


def set_budget(user_id: int, data: dict) -> Budget:
    """Set or update budget for a category."""
    month = data.get('month', datetime.now().month)
    year = data.get('year', datetime.now().year)
    category = data['category']
    limit = float(data['monthly_limit'])

    existing = Budget.query.filter_by(
        user_id=user_id,
        category=category,
        month=month,
        year=year
    ).first()

    if existing:
        existing.monthly_limit = limit
        db.session.commit()
        return existing

    budget = Budget(
        user_id=user_id,
        category=category,
        monthly_limit=limit,
        month=month,
        year=year
    )
    db.session.add(budget)
    db.session.commit()
    return budget


def get_budget_summary(user_id: int) -> list:
    """Compare budgets against actual spending for current month."""
    now = datetime.now()
    budgets = Budget.query.filter_by(
        user_id=user_id,
        month=now.month,
        year=now.year
    ).all()

    expenses = Expense.query.filter(
        Expense.user_id == user_id,
        db.extract('month', Expense.date) == now.month,
        db.extract('year', Expense.date) == now.year
    ).all()

    actual_spending = defaultdict(float)
    for expense in expenses:
        cat = expense.predicted_category or 'Uncategorized'
        actual_spending[cat] += expense.amount

    summary = []
    for budget in budgets:
        spent = actual_spending.get(budget.category, 0.0)
        remaining = budget.monthly_limit - spent
        usage_pct = (spent / budget.monthly_limit * 100) if budget.monthly_limit > 0 else 0

        summary.append({
            'id': budget.id,
            'category': budget.category,
            'budget_limit': round(budget.monthly_limit, 2),
            'spent': round(spent, 2),
            'remaining': round(remaining, 2),
            'usage_percentage': round(usage_pct, 1),
            'status': 'over_budget' if spent > budget.monthly_limit else (
                'warning' if usage_pct >= 80 else 'on_track'
            ),
            'alert': spent > budget.monthly_limit
        })

    return sorted(summary, key=lambda x: x['usage_percentage'], reverse=True)


def update_budget(user_id: int, budget_id: int, data: dict) -> Budget | None:
    budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
    if budget is None:
        return None

    if 'category' in data and data['category']:
        budget.category = data['category']

    if 'monthly_limit' in data:
        budget.monthly_limit = float(data['monthly_limit'])

    if 'month' in data and data['month']:
        budget.month = int(data['month'])

    if 'year' in data and data['year']:
        budget.year = int(data['year'])

    db.session.commit()
    return budget


def delete_budget(user_id: int, budget_id: int) -> bool:
    budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
    if budget is None:
        return False

    db.session.delete(budget)
    db.session.commit()
    return True


def suggest_budgets(user_id: int) -> list:
    """Auto-suggest budgets based on past 3 months spending."""
    expenses = Expense.query.filter_by(user_id=user_id).all()

    category_totals = defaultdict(list)
    for expense in expenses:
        cat = expense.predicted_category or 'Uncategorized'
        month_key = (expense.date.year, expense.date.month)
        category_totals[cat].append((month_key, expense.amount))

    suggestions = []
    for cat, data in category_totals.items():
        monthly = defaultdict(float)
        for key, amount in data:
            monthly[key] += amount

        recent = sorted(monthly.items())[-3:]
        avg = sum(v for _, v in recent) / len(recent)
        suggested_limit = round(avg * 1.1, 2)  # 10% buffer

        suggestions.append({
            'category': cat,
            'avg_spending': round(avg, 2),
            'suggested_limit': suggested_limit,
            'basis': f"Based on last {len(recent)} months average"
        })

    return sorted(suggestions, key=lambda x: x['avg_spending'], reverse=True)
