import os
from datetime import datetime

import joblib

from app import db
from app.models import Category, Expense, CategoryCorrection
from app.ml_models.semantic_classifier import predict_category_semantic

ML_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml_models")

MODEL_CANDIDATES = (
    os.path.join(ML_DIR, "model.pkl"),
    os.path.join(ML_DIR, "naive_bayes_model.pkl"),
)

CANONICAL_CATEGORIES = {
    "food": "Food",
    "transport": "Transport",
    "travel": "Transport",
    "bills": "Bills",
    "shopping": "Shopping",
    "entertainment": "Entertainment",
    "health": "Health",
    "uncategorized": "Uncategorized",
}

KEYWORD_CATEGORY_MAP = {
    "food": {
        "food", "grocery", "groceries", "restaurant", "swiggy", "zomato", "meal",
        "breakfast", "lunch", "dinner", "snack", "snacks", "bakery",
    },
    "transport": {
        "transport", "travel", "cab", "taxi", "uber", "ola", "metro", "bus", "train",
        "fuel", "petrol", "diesel", "flight", "airfare", "ticket", "auto",
    },
    "bills": {
        "bill", "bills", "electricity", "water", "gas", "internet", "wifi", "broadband",
        "recharge", "postpaid", "prepaid", "rent", "emi", "loan", "utility",
    },
    "shopping": {
        "shopping", "shop", "amazon", "flipkart", "myntra", "ajio", "meesho",
        "clothes", "fashion", "electronics", "purchase", "buy",
    },
    "entertainment": {
        "entertainment", "movie", "cinema", "netflix", "prime", "hotstar", "spotify",
        "concert", "game", "gaming", "show", "theatre",
    },
    "health": {
        "health", "hospital", "doctor", "pharmacy", "medicine", "medical", "dental",
        "clinic", "insurance", "checkup", "gym", "fitness",
    },
}

_model = None

for path in MODEL_CANDIDATES:
    if os.path.exists(path):
        try:
            _model = joblib.load(path)
            break
        except Exception:
            continue


def _parse_date(value):
    if not value:
        return datetime.utcnow().date()

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        return datetime.utcnow().date()

    return value


def _normalize_category(value: str | None) -> str:
    text = (value or "").strip()
    if not text:
        return "Uncategorized"

    canonical = CANONICAL_CATEGORIES.get(text.lower())
    if canonical:
        return canonical

    return text.title()


def _keyword_category(description: str) -> str | None:
    tokens = [token.strip(".,!?()[]{}:;\"'").lower() for token in description.split()]
    tokens = [token for token in tokens if token]

    for canonical_key, keywords in KEYWORD_CATEGORY_MAP.items():
        if any(token in keywords for token in tokens):
            return _normalize_category(canonical_key)
    return None


def predict_category(description: str):
    # Kept for reference/rollback: old keyword-map + Naive Bayes fallback
    # if _model is None:
    #     return "Uncategorized", 0.0
    # text = (description or "").strip().lower()
    # if not text:
    #     return "Uncategorized", 0.0
    # keyword_match = _keyword_category(text)
    # if keyword_match:
    #     return keyword_match, 0.95
    # try:
    #     predicted = _model.predict([text])[0]
    #     confidence = 1.0
    #     if hasattr(_model, "predict_proba"):
    #         probabilities = _model.predict_proba([text])[0]
    #         confidence = float(max(probabilities))
    #         if confidence < 0.4:
    #             predicted = "Uncategorized"
    #     return _normalize_category(str(predicted)), round(confidence, 3)
    # except Exception:
    #     return "Uncategorized", 0.0

    result = predict_category_semantic(description)
    return _normalize_category(result["category"]), result["confidence"]

def add_expense(user_id: int, data: dict) -> Expense:
    description = (data.get("description") or "").strip()
    if not description:
        raise ValueError("Description is required")

    try:
        amount = float(data["amount"])
    except (KeyError, ValueError):
        raise ValueError("Valid amount is required")

    expense_date = _parse_date(data.get("date"))
    predicted_category, confidence = predict_category(description)

    category = Category.query.filter(
        db.func.lower(Category.name) == predicted_category.lower()
    ).first()

    if category is None and predicted_category != "Uncategorized":
        category = Category(name=predicted_category)
        db.session.add(category)
        db.session.flush()

    if category is None:
        category = Category.query.filter(
            db.func.lower(Category.name) == "uncategorized"
        ).first()

    expense = Expense(
        user_id=user_id,
        category_id=category.id if category else None,
        description=description,
        amount=amount,
        date=expense_date,
        predicted_category=predicted_category,
        confidence=confidence,
    )

    db.session.add(expense)
    db.session.commit()

    return expense


def get_user_expenses(user_id: int):
    return (
        Expense.query.filter_by(user_id=user_id)
        .order_by(Expense.date.desc(), Expense.created_at.desc())
        .all()
    )


def delete_expense(user_id: int, expense_id: int) -> bool:
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    if expense is None:
        return False

    db.session.delete(expense)
    db.session.commit()
    return True


def log_correction(user_id: int, expense_id: int, corrected_category: str) -> Expense:
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    if expense is None:
        raise ValueError("Expense not found")

    predicted_category = expense.category.name if expense.category else expense.predicted_category
    
    category_obj = Category.query.filter(
        db.func.lower(Category.name) == corrected_category.lower()
    ).first()
    
    if category_obj is None and corrected_category != "Uncategorized":
        category_obj = Category(name=corrected_category)
        db.session.add(category_obj)
        db.session.flush()
        
    if category_obj is None:
        category_obj = Category.query.filter(
            db.func.lower(Category.name) == "uncategorized"
        ).first()

    expense.category_id = category_obj.id if category_obj else None

    correction = CategoryCorrection(
        user_id=user_id,
        description=expense.description,
        predicted_category=predicted_category,
        corrected_category=corrected_category
    )
    db.session.add(correction)
    db.session.commit()
    return expense
