import pytest
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import os
from unittest.mock import patch, MagicMock

from app.services.query_service import parse_query, execute_query, format_response, _parse_time_period
from app.models import Expense, Category, User

# For DB execution tests
from app import create_app, db

@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Insert a User so foreign key constraints pass
        user = User.query.get(1)
        if not user:
            user = User(id=1, name="Test User", email="test@test.com", password_hash="test")
            db.session.add(user)
        
        cat_food = Category.query.filter_by(name='Food').first()
        if not cat_food:
            cat_food = Category(name='Food')
            db.session.add(cat_food)
            
        cat_transport = Category.query.filter_by(name='Transport').first()
        if not cat_transport:
            cat_transport = Category(name='Transport')
            db.session.add(cat_transport)
            
        db.session.commit()
        
        today = datetime.utcnow().date()
        this_month_start = today.replace(day=1)
        last_month_start = this_month_start - relativedelta(months=1)
        
        # Add test expenses
        expenses = [
            Expense(user_id=1, category_id=cat_food.id, description="Burger", amount=150.0, date=this_month_start),
            Expense(user_id=1, category_id=cat_food.id, description="Pizza", amount=300.0, date=this_month_start),
            Expense(user_id=1, category_id=cat_transport.id, description="Uber", amount=200.0, date=last_month_start),
            Expense(user_id=1, category_id=cat_transport.id, description="Bus", amount=50.0, date=last_month_start),
            Expense(user_id=1, category_id=None, predicted_category='Shopping', description="Shirt", amount=1000.0, date=this_month_start)
        ]
        db.session.add_all(expenses)
        db.session.commit()
        
        yield app

def test_parse_query_intents():
    # 1. total_by_category
    res = parse_query("how much did I spend on food this month")
    assert res["intent"] == "total_by_category"
    assert res["category"] == "Food"
    
    # 2. total_by_period
    res = parse_query("how much did I spend last month")
    assert res["intent"] == "total_by_period"
    
    # 3. highest_expense
    res = parse_query("what was my biggest expense in june")
    assert res["intent"] == "highest_expense"
    
    # 4. compare_periods
    res = parse_query("compare my transport spending this month vs last month")
    assert res["intent"] == "compare_periods"
    assert res["comparison"] is True
    assert res["category"] == "Transport"
    
    # 4a. compare_periods directional 1
    res1 = parse_query("compare this month vs last month")
    
    # 4b. compare_periods directional 2
    res2 = parse_query("compare last month vs this month")
    
    # They should have the opposite order of parsed periods
    assert res1["time_period"][0] == res2["time_period"][1]
    assert res1["time_period"][1] == res2["time_period"][0]
    
    # And check the actual dates
    today = datetime.utcnow().date()
    this_month_start = today.replace(day=1)
    last_month_start = this_month_start - relativedelta(months=1)
    assert res1["time_period"][0][0] == this_month_start
    assert res1["time_period"][1][0] == last_month_start
    
    # 5. category_breakdown
    res = parse_query("category breakdown for this year")
    assert res["intent"] == "category_breakdown"
    
    # 6. unknown (ambiguous/gibberish)
    res = parse_query("xyzzy foobar blargh")
    assert res["intent"] == "unknown"


def test_execute_query(test_app):
    today = datetime.utcnow().date()
    this_month_start = today.replace(day=1)
    next_month_start = this_month_start + relativedelta(months=1)
    this_month_end = next_month_start - timedelta(days=1)
    
    last_month_start = this_month_start - relativedelta(months=1)
    last_month_end = this_month_start - timedelta(days=1)

    # test total_by_category (Food this month)
    res = execute_query(1, {
        "intent": "total_by_category",
        "category": "Food",
        "time_period": (this_month_start, this_month_end)
    })
    assert res["total"] == 450.0

    # test total_by_period (last month)
    res = execute_query(1, {
        "intent": "total_by_period",
        "time_period": (last_month_start, last_month_end)
    })
    assert res["total"] == 250.0

    # test highest_expense (this month)
    res = execute_query(1, {
        "intent": "highest_expense",
        "time_period": (this_month_start, this_month_end)
    })
    assert res["amount"] == 1000.0
    assert res["category"] == "Shopping"

    # test category_breakdown (this month)
    res = execute_query(1, {
        "intent": "category_breakdown",
        "time_period": (this_month_start, this_month_end)
    })
    assert res["breakdown"]["Shopping"] == 1000.0
    assert res["breakdown"]["Food"] == 450.0

    # test compare_periods (this month vs last month)
    res = execute_query(1, {
        "intent": "compare_periods",
        "time_period": [(this_month_start, this_month_end), (last_month_start, last_month_end)]
    })
    assert res["period1_total"] == 1450.0  # Food(450) + Shopping(1000)
    assert res["period2_total"] == 250.0   # Transport(250)
    assert res["difference"] == 1200.0


def test_format_response_fallback():
    parsed = {"intent": "total_by_category"}
    result = {"category": "Food", "start_date": "2026-09-01", "end_date": "2026-09-30", "total": 450.0}
    
    res = format_response(parsed, result)
    assert "You spent ₹450.0 on Food between 2026-09-01 and 2026-09-30." in res
    
    # Test unknown
    res = format_response({"intent": "unknown"}, {})
    assert "I couldn't understand that question." in res


@patch('app.services.query_service.requests.post')
@patch.dict(os.environ, {"LLM_PHRASING_ENABLED": "true"})
def test_ollama_phrasing(mock_post):
    parsed = {"intent": "total_by_category"}
    result = {"category": "Food", "start_date": "2026-09-01", "end_date": "2026-09-30", "total": 450.0}
    
    # Setup mock response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"response": "You spent a total of ₹450.0 on Food from Sep 1 to Sep 30."}
    mock_post.return_value = mock_resp
    
    output = format_response(parsed, result)
    
    # Assert requests.post was called
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "localhost:11434" in args[0]
    
    # Assert prompt verbatim contains result dict
    prompt = kwargs['json']['prompt']
    assert str(result) in prompt
    assert "Do not add, remove, or alter any numbers" in prompt
    
    # Assert it returns the mocked response
    assert output == "You spent a total of ₹450.0 on Food from Sep 1 to Sep 30."


@patch('app.services.query_service.requests.post')
@patch.dict(os.environ, {"LLM_PHRASING_ENABLED": "true"})
def test_ollama_phrasing_fallback_on_error(mock_post):
    parsed = {"intent": "total_by_category"}
    result = {"category": "Food", "start_date": "2026-09-01", "end_date": "2026-09-30", "total": 450.0}
    
    mock_post.side_effect = Exception("Connection Refused")
    
    # Should not crash, should return fallback
    output = format_response(parsed, result)
    assert "You spent ₹450.0 on Food" in output
