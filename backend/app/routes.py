from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app import db
from app.models import User, Expense, Budget, Category, ForecastResult
from app.services.expense_service import add_expense, get_user_expenses, delete_expense, log_correction
from app.services.forecast_service import forecast_spending
from app.services.query_service import parse_query, execute_query, format_response
from app.services.budget_service import (
    delete_budget,
    get_budget_summary,
    set_budget,
    update_budget,
)
from app.schemas.expense_schema import ExpenseSchema
from app.schemas.user_schema import UserSchema
from app.utils.validators import validate_budget_input, validate_expense_input, validate_user_input
from datetime import date, datetime, timedelta
import calendar

main = Blueprint('main', __name__)
expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)

# ─────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────

@main.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    error = validate_user_input(data)
    if error:
        return jsonify({'error': error}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(name=data['name'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully', 'user_id': user.id}), 201


@main.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if not user or not user.check_password(data.get('password', '')):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'access_token': token,
        'user': {'id': user.id, 'name': user.name, 'email': user.email}
    }), 200


# ─────────────────────────────────────────
# EXPENSE ROUTES
# ─────────────────────────────────────────

@main.route('/api/expenses', methods=['POST'])
@jwt_required()
def create_expense():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    error = validate_expense_input(data)
    if error:
        return jsonify({'error': error}), 400

    try:
        expense = add_expense(user_id, data)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Unable to save expense right now. Please try again.'}), 500

    return jsonify({
        'message': 'Expense added',
        'expense': expense.to_dict()
    }), 201


@main.route('/api/expenses', methods=['GET'])
@jwt_required()
def get_expenses():
    user_id = int(get_jwt_identity())
    expenses = get_user_expenses(user_id)
    return jsonify({'expenses': [e.to_dict() for e in expenses]}), 200


@main.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def remove_expense(expense_id):
    user_id = int(get_jwt_identity())
    result = delete_expense(user_id, expense_id)
    if not result:
        return jsonify({'error': 'Expense not found'}), 404
    return jsonify({'message': 'Expense deleted successfully'}), 200


@main.route('/api/expenses/<int:expense_id>/category', methods=['PUT'])
@jwt_required()
def correct_expense_category(expense_id):
    data = request.get_json() or {}
    corrected_category = data.get('category')
    if not corrected_category:
        return jsonify({'error': 'Category is required'}), 400

    user_id = int(get_jwt_identity())
    try:
        expense = log_correction(user_id, expense_id, corrected_category)
        return jsonify({
            'message': 'Category corrected',
            'expense': expense.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


# ─────────────────────────────────────────
# FORECAST ROUTES
# ─────────────────────────────────────────

@main.route('/api/forecast', methods=['GET'])
@jwt_required()
def get_forecast():
    user_id = int(get_jwt_identity())
    result = forecast_spending(user_id)
    return jsonify(result), 200


# ─────────────────────────────────────────
# BUDGET ROUTES
# ─────────────────────────────────────────

@main.route('/api/budget', methods=['POST'])
@jwt_required()
def create_budget():
    data = request.get_json()
    user_id = int(get_jwt_identity())
    error = validate_budget_input(data)
    if error:
        return jsonify({'error': error}), 400

    budget = set_budget(user_id, data)
    return jsonify({'message': 'Budget set', 'budget': budget.to_dict()}), 201


@main.route('/api/budget/<int:budget_id>', methods=['PUT'])
@jwt_required()
def modify_budget(budget_id):
    data = request.get_json() or {}
    user_id = int(get_jwt_identity())

    if 'monthly_limit' in data:
        try:
            limit = float(data['monthly_limit'])
            if limit <= 0:
                return jsonify({'error': 'Monthly limit must be greater than 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Monthly limit must be a valid number'}), 400

    budget = update_budget(user_id, budget_id, data)
    if budget is None:
        return jsonify({'error': 'Budget not found'}), 404

    return jsonify({'message': 'Budget updated', 'budget': budget.to_dict()}), 200


@main.route('/api/budget/<int:budget_id>', methods=['DELETE'])
@jwt_required()
def remove_budget(budget_id):
    user_id = int(get_jwt_identity())
    deleted = delete_budget(user_id, budget_id)
    if not deleted:
        return jsonify({'error': 'Budget not found'}), 404
    return jsonify({'message': 'Budget deleted'}), 200


@main.route('/api/budget/summary', methods=['GET'])
@jwt_required()
def budget_summary():
    user_id = int(get_jwt_identity())
    summary = get_budget_summary(user_id)
    return jsonify({'summary': summary}), 200


# ─────────────────────────────────────────
# DASHBOARD ROUTE
# ─────────────────────────────────────────

@main.route('/api/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    def get_period_bounds(period: str, today: date):
        if period == 'weekly':
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            prev_start = start - timedelta(days=7)
            prev_end = start - timedelta(days=1)
            return (start, end), (prev_start, prev_end)

        if period == 'yearly':
            start = date(today.year, 1, 1)
            end = date(today.year, 12, 31)
            prev_start = date(today.year - 1, 1, 1)
            prev_end = date(today.year - 1, 12, 31)
            return (start, end), (prev_start, prev_end)

        # monthly default
        start = date(today.year, today.month, 1)
        end = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        if today.month == 1:
            prev_year, prev_month = today.year - 1, 12
        else:
            prev_year, prev_month = today.year, today.month - 1
        prev_start = date(prev_year, prev_month, 1)
        prev_end = date(prev_year, prev_month, calendar.monthrange(prev_year, prev_month)[1])
        return (start, end), (prev_start, prev_end)

    def in_bounds(expense_date: date, bounds: tuple[date, date]) -> bool:
        return bounds[0] <= expense_date <= bounds[1]

    def trend_from_totals(current_total: float, previous_total: float):
        if current_total == 0 and previous_total == 0:
            return 'flat', 'No change'
        if previous_total == 0 and current_total > 0:
            return 'up', 'New spend period'

        delta_pct = ((current_total - previous_total) / previous_total) * 100 if previous_total else 0
        if abs(delta_pct) < 1:
            return 'flat', 'Flat vs previous period'
        if delta_pct > 0:
            return 'up', f'+{round(delta_pct, 1)}% vs previous period'
        return 'down', f'{round(delta_pct, 1)}% vs previous period'

    def forecast_value_for_period(period: str, current_total: float, all_expenses: list, model_forecast: dict):
        if period == 'weekly':
            return round(current_total, 2), 'Next week'

        if period == 'yearly':
            today = datetime.utcnow().date()
            months_elapsed = max(1, today.month)
            return round((current_total / months_elapsed) * 12, 2), 'Projected year total'

        # monthly default
        predicted_total = model_forecast.get('predicted_total') if isinstance(model_forecast, dict) else None
        if isinstance(predicted_total, (int, float)):
            return round(float(predicted_total), 2), 'Next month'
        return round(current_total, 2), 'Next month'

    user_id = int(get_jwt_identity())
    period = (request.args.get('period') or 'monthly').strip().lower()
    if period not in ('weekly', 'monthly', 'yearly'):
        period = 'monthly'

    today = datetime.utcnow().date()
    current_bounds, previous_bounds = get_period_bounds(period, today)
    all_expenses = get_user_expenses(user_id)
    current_period_expenses = [e for e in all_expenses if in_bounds(e.date, current_bounds)]
    previous_period_expenses = [e for e in all_expenses if in_bounds(e.date, previous_bounds)]

    current_total = sum(e.amount for e in current_period_expenses)
    previous_total = sum(e.amount for e in previous_period_expenses)
    trend_code, trend_label = trend_from_totals(current_total, previous_total)

    forecast = forecast_spending(user_id)
    forecast_value, forecast_label = forecast_value_for_period(period, current_total, all_expenses, forecast)
    summary = get_budget_summary(user_id)

    return jsonify({
        'period': period,
        'total_expenses': round(current_total, 2),
        'expense_count': len(current_period_expenses),
        'forecast_value': forecast_value,
        'forecast_label': forecast_label,
        'trend': trend_code,
        'trend_label': trend_label,
        'forecast': forecast,
        'budget_summary': summary
    }), 200


@main.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'SmartSpend API is running ✅'}), 200

# ─────────────────────────────────────────
# QUERY ROUTES
# ─────────────────────────────────────────

@main.route('/api/query', methods=['POST'])
@jwt_required()
def query_endpoint():
    """
    Expected Request: {"question": "how much did I spend on food last month"}
    Expected Response: {"question": "...", "intent": "...", "answer": "...", "data": {...}}
    """
    data = request.get_json() or {}
    question = data.get('question')
    if not question:
        return jsonify({'error': 'Question is required'}), 400
        
    user_id = int(get_jwt_identity())
    
    parsed = parse_query(question)
    if parsed["intent"] == "unknown":
        answer = format_response(parsed, {})
        return jsonify({
            "question": question,
            "intent": "unknown",
            "answer": answer,
            "data": None
        }), 200
        
    result = execute_query(user_id, parsed)
    answer = format_response(parsed, result)
    
    return jsonify({
        "question": question,
        "intent": parsed["intent"],
        "answer": answer,
        "data": result
    }), 200
