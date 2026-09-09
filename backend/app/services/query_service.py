import os
import re
import requests
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func

from app import db
from app.models import Expense, Category
from app.ml_models.semantic_classifier import predict_category_semantic


def _parse_time_period(text: str) -> tuple[date, date]:
    """Parse relative time periods into precise (start_date, end_date) tuples."""
    text = text.lower()
    today = datetime.utcnow().date()
    
    if "this month" in text:
        start = today.replace(day=1)
        next_month = start + relativedelta(months=1)
        end = next_month - timedelta(days=1)
        return start, end
        
    if "last month" in text:
        start = (today.replace(day=1) - relativedelta(months=1))
        end = today.replace(day=1) - timedelta(days=1)
        return start, end
        
    if "this year" in text:
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
        return start, end
        
    if "last year" in text:
        start = today.replace(year=today.year - 1, month=1, day=1)
        end = today.replace(year=today.year - 1, month=12, day=31)
        return start, end
        
    match = re.search(r"last (\d+) months?", text)
    if match:
        months = int(match.group(1))
        start = today - relativedelta(months=months)
        return start, today
        
    # Month names
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4, 
        "may": 5, "june": 6, "july": 7, "august": 8, 
        "september": 9, "october": 10, "november": 11, "december": 12,
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, 
        "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    
    for month_name, month_num in months.items():
        if month_name in text:
            # Assume current year unless specified
            year = today.year
            start = date(year, month_num, 1)
            end = start + relativedelta(months=1) - timedelta(days=1)
            # If the month is in the future, assume they meant last year
            if start > today:
                start = start.replace(year=year - 1)
                end = end.replace(year=year - 1)
            return start, end
            
    # Default to "this month" if no period found but query exists
    start = today.replace(day=1)
    next_month = start + relativedelta(months=1)
    end = next_month - timedelta(days=1)
    return start, end


def parse_query(text: str) -> dict:
    """Extract intent, category, time period, and comparison flags from natural language."""
    text_lower = text.lower()
    
    # 1. Detect Category via Semantic Model
    # Since semantic_classifier handles natural language well, we pass the query.
    # It will extract the strongest category concept if confidence is high.
    sem_result = predict_category_semantic(text)
    category = sem_result["category"] if sem_result["category"] != "Uncategorized" else None

    # 2. Detect Comparison
    comparison = "compare" in text_lower or "vs" in text_lower or "versus" in text_lower

    # 3. Detect Intent
    intent = "unknown"
    if comparison:
        intent = "compare_periods"
    elif "highest" in text_lower or "biggest" in text_lower or "most expensive" in text_lower or "largest" in text_lower:
        intent = "highest_expense"
    elif "breakdown" in text_lower or "by category" in text_lower or "where did my money go" in text_lower:
        intent = "category_breakdown"
    elif "how much" in text_lower or "total" in text_lower or "spent" in text_lower:
        if category:
            intent = "total_by_category"
        else:
            intent = "total_by_period"
            
    if intent == "unknown":
        return {"intent": "unknown"}
        
    # 4. Extract Date Range(s)
    if intent == "compare_periods":
        # Recognized literal phrases
        literal_phrases = ["this month", "last month", "this year", "last year"]
        months_full = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
        months_abbr = ["jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
        
        found_periods = []
        
        # Check literals
        for p in literal_phrases + months_full + months_abbr:
            idx = text_lower.find(p)
            if idx != -1:
                found_periods.append((idx, p))
                
        # Check regex
        for m in re.finditer(r"last (\d+) months?", text_lower):
            found_periods.append((m.start(), m.group(0)))
            
        # Sort by position
        found_periods.sort(key=lambda x: x[0])
        
        # Extract unique parsed dates based on order
        unique_parsed_dates = []
        for idx, phrase in found_periods:
            parsed_date = _parse_time_period(phrase)
            if parsed_date not in unique_parsed_dates:
                unique_parsed_dates.append(parsed_date)
                
        if len(unique_parsed_dates) >= 2:
            time_period = [unique_parsed_dates[0], unique_parsed_dates[1]]
        else:
            # Fallback to current vs previous month if generic compare
            today = datetime.utcnow().date()
            start1 = today.replace(day=1)
            end1 = start1 + relativedelta(months=1) - timedelta(days=1)
            start2 = start1 - relativedelta(months=1)
            end2 = start1 - timedelta(days=1)
            time_period = [(start1, end1), (start2, end2)]
    else:
        time_period = _parse_time_period(text_lower)

    return {
        "intent": intent,
        "category": category,
        "time_period": time_period,
        "comparison": comparison
    }


def execute_query(user_id: int, parsed: dict) -> dict:
    """Execute raw SQL aggregation based on parsed query slots."""
    intent = parsed["intent"]
    
    if intent == "unknown":
        return {}
        
    if intent == "compare_periods":
        # Expected time_period is list of two tuples
        period1, period2 = parsed["time_period"]
        
        # Period 1
        q1 = db.session.query(func.sum(Expense.amount)).select_from(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= period1[0],
            Expense.date <= period1[1]
        )
        # Period 2
        q2 = db.session.query(func.sum(Expense.amount)).select_from(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= period2[0],
            Expense.date <= period2[1]
        )
        
        # Add category filter if present
        if parsed.get("category"):
            cat = parsed["category"].lower()
            q1 = q1.outerjoin(Category).filter(
                db.or_(
                    func.lower(Category.name) == cat,
                    func.lower(Expense.predicted_category) == cat
                )
            )
            q2 = q2.outerjoin(Category).filter(
                db.or_(
                    func.lower(Category.name) == cat,
                    func.lower(Expense.predicted_category) == cat
                )
            )

        val1 = q1.scalar() or 0.0
        val2 = q2.scalar() or 0.0
        
        delta = val1 - val2
        pct = (delta / val2 * 100) if val2 > 0 else 0.0
        
        return {
            "period1_start": str(period1[0]),
            "period1_end": str(period1[1]),
            "period1_total": round(val1, 2),
            "period2_start": str(period2[0]),
            "period2_end": str(period2[1]),
            "period2_total": round(val2, 2),
            "difference": round(delta, 2),
            "percentage_change": round(pct, 1),
            "category": parsed.get("category")
        }

    # All other intents have a single time period tuple
    start_date, end_date = parsed["time_period"]
    
    base_query = db.session.query(Expense).select_from(Expense).filter(
        Expense.user_id == user_id,
        Expense.date >= start_date,
        Expense.date <= end_date
    )

    if intent == "total_by_category":
        cat = parsed["category"].lower()
        val = db.session.query(func.sum(Expense.amount)).select_from(Expense).outerjoin(Category).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date,
            db.or_(
                func.lower(Category.name) == cat,
                func.lower(Expense.predicted_category) == cat
            )
        ).scalar() or 0.0
        return {
            "category": parsed["category"],
            "start_date": str(start_date),
            "end_date": str(end_date),
            "total": round(val, 2)
        }
        
    elif intent == "total_by_period":
        val = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date
        ).scalar() or 0.0
        return {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "total": round(val, 2)
        }
        
    elif intent == "highest_expense":
        highest = base_query.order_by(Expense.amount.desc()).first()
        if highest:
            return {
                "start_date": str(start_date),
                "end_date": str(end_date),
                "amount": round(highest.amount, 2),
                "description": highest.description,
                "date": str(highest.date),
                "category": highest.category.name if highest.category else highest.predicted_category
            }
        return {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "amount": 0.0,
            "description": None,
            "date": None,
            "category": None
        }
        
    elif intent == "category_breakdown":
        # Group by category logic
        expenses = base_query.all()
        breakdown = {}
        for e in expenses:
            cat_name = e.category.name if e.category else e.predicted_category
            if not cat_name:
                cat_name = "Uncategorized"
            breakdown[cat_name] = breakdown.get(cat_name, 0.0) + e.amount
            
        sorted_breakdown = dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))
        
        return {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "breakdown": {k: round(v, 2) for k, v in sorted_breakdown.items()}
        }

    return {}


def format_response(parsed: dict, result: dict) -> str:
    """Format raw SQL aggregations into natural sentences, optionally via LLM."""
    intent = parsed["intent"]
    
    if intent == "unknown":
        return "I couldn't understand that question. Try asking about totals, categories, or comparisons."
        
    # Build default fallback template
    fallback = ""
    if intent == "total_by_category":
        fallback = f"You spent ₹{result['total']} on {result['category']} between {result['start_date']} and {result['end_date']}."
    elif intent == "total_by_period":
        fallback = f"You spent a total of ₹{result['total']} between {result['start_date']} and {result['end_date']}."
    elif intent == "highest_expense":
        if result['amount'] > 0:
            fallback = f"Your highest expense was ₹{result['amount']} for '{result['description']}' on {result['date']}."
        else:
            fallback = f"You had no expenses between {result['start_date']} and {result['end_date']}."
    elif intent == "category_breakdown":
        if not result['breakdown']:
            fallback = f"No expenses found between {result['start_date']} and {result['end_date']}."
        else:
            top_cat = list(result['breakdown'].keys())[0]
            top_amt = result['breakdown'][top_cat]
            fallback = f"You spent across {len(result['breakdown'])} categories, with the highest being {top_cat} at ₹{top_amt}."
    elif intent == "compare_periods":
        cat_str = f" on {result['category']}" if result.get("category") else ""
        direction = "more" if result['difference'] > 0 else "less"
        abs_diff = abs(result['difference'])
        fallback = f"You spent ₹{result['period1_total']}{cat_str} in the recent period vs ₹{result['period2_total']} previously (₹{abs_diff} {direction})."

    # Optional LLM phrasing
    if os.environ.get("LLM_PHRASING_ENABLED", "").lower() == "true":
        try:
            prompt = f"Rephrase this data into one natural sentence. Do not add, remove, or alter any numbers: {result}"
            payload = {
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
            res = requests.post("http://localhost:11434/api/generate", json=payload, timeout=2.0)
            if res.status_code == 200:
                data = res.json()
                if "response" in data:
                    return data["response"].strip()
        except Exception:
            # Silently fallback
            pass
            
    return fallback
