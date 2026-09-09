from app import db
from datetime import datetime
import bcrypt


# =====================================================
# USER MODEL
# =====================================================

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    expenses = db.relationship(
        'Expense',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan'
    )

    budgets = db.relationship(
        'Budget',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan'
    )

    forecasts = db.relationship(
        'ForecastResult',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def __repr__(self):
        return f'<User {self.email}>'


# =====================================================
# CATEGORY MODEL
# =====================================================

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    expenses = db.relationship(
        'Expense',
        backref='category',
        lazy=True
    )

    def __repr__(self):
        return f'<Category {self.name}>'


# =====================================================
# EXPENSE MODEL (ML Integrated)
# =====================================================

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.id'),
        nullable=True
    )

    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    date = db.Column(
        db.Date,
        default=lambda: datetime.utcnow().date(),
        nullable=False
    )

    # 🔥 ML Prediction Fields
    predicted_category = db.Column(db.String(50), nullable=True)
    confidence = db.Column(db.Float, nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "description": self.description,
            "amount": self.amount,
            "date": str(self.date),
            "category": self.category.name if self.category else self.predicted_category,
            "confidence": self.confidence,
            "created_at": str(self.created_at)
        }

    def __repr__(self):
        return f'<Expense {self.description} ₹{self.amount}>'


# =====================================================
# BUDGET MODEL
# =====================================================

class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    category = db.Column(db.String(50), nullable=False)
    monthly_limit = db.Column(db.Float, nullable=False)

    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category": self.category,
            "monthly_limit": self.monthly_limit,
            "month": self.month,
            "year": self.year
        }

    def __repr__(self):
        return f'<Budget {self.category} ₹{self.monthly_limit}>'


# =====================================================
# FORECAST RESULT MODEL
# =====================================================

class ForecastResult(db.Model):
    __tablename__ = 'forecast_results'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    predicted_month = db.Column(db.Integer, nullable=False)
    predicted_year = db.Column(db.Integer, nullable=False)
    predicted_amount = db.Column(db.Float, nullable=False)

    generated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "predicted_month": self.predicted_month,
            "predicted_year": self.predicted_year,
            "predicted_amount": round(self.predicted_amount, 2),
            "generated_at": str(self.generated_at)
        }

    def __repr__(self):
        return f'<Forecast ₹{self.predicted_amount}>'


# =====================================================
# CATEGORY CORRECTION MODEL (Active Learning)
# =====================================================

class CategoryCorrection(db.Model):
    __tablename__ = 'category_corrections'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    description = db.Column(db.String(255), nullable=False)
    predicted_category = db.Column(db.String(50), nullable=False)
    corrected_category = db.Column(db.String(50), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "description": self.description,
            "predicted_category": self.predicted_category,
            "corrected_category": self.corrected_category,
            "created_at": str(self.created_at)
        }

    def __repr__(self):
        return f'<CategoryCorrection {self.predicted_category} -> {self.corrected_category}>'