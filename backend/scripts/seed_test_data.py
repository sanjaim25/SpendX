import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import random
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict

from app import create_app, db
from app.models import User, Category, Expense

def generate_random_date(start_date: date, end_date: date) -> date:
    """Generate a random date between start_date and end_date."""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates + 1)
    return start_date + timedelta(days=random_number_of_days)

def seed_data():
    app = create_app()
    with app.app_context():
        # Ensure categories exist
        category_names = ['Food', 'Transport', 'Bills', 'Shopping', 'Entertainment', 'Health']
        categories = {}
        for name in category_names:
            cat = Category.query.filter(Category.name.ilike(name)).first()
            if not cat:
                cat = Category(name=name)
                db.session.add(cat)
                db.session.commit()
            categories[name] = cat
            
        # Get or create test user
        email = "test@example.com"
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name="Test User", email=email)
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            print(f"Created new test user: {email}")
        else:
            print(f"Using existing test user: {email}")
            
        # Delete existing expenses for this user
        deleted_count = Expense.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        print(f"Deleted {deleted_count} existing expenses for {email}")
        
        # Determine date ranges for the 3 months
        today = datetime.utcnow().date()
        
        this_month_start = today.replace(day=1)
        this_month_end = today # Up to today
        if this_month_start == this_month_end:
            # Avoid ValueError in randrange if today is the 1st
            this_month_end = this_month_start + timedelta(days=1)
            
        last_month_start = this_month_start - relativedelta(months=1)
        last_month_end = this_month_start - timedelta(days=1)
        
        month_before_start = last_month_start - relativedelta(months=1)
        month_before_end = last_month_start - timedelta(days=1)
        
        months = [
            ("This Month", this_month_start, this_month_end),
            ("Last Month", last_month_start, last_month_end),
            ("Month Before", month_before_start, month_before_end)
        ]
        
        category_amount_ranges = {
            'Food': (50, 800),
            'Transport': (20, 500),
            'Bills': (500, 3000),
            'Shopping': (200, 5000),
            'Entertainment': (300, 2500),
            'Health': (100, 4000)
        }
        
        descriptions = {
            'Food': ["Lunch", "Dinner at Restaurant", "Groceries", "Coffee", "Snacks"],
            'Transport': ["Uber/Ola", "Metro Pass", "Fuel", "Bus Ticket", "Auto Rickshaw"],
            'Bills': ["Electricity Bill", "Internet", "Water Bill", "Phone Recharge", "Rent"],
            'Shopping': ["Clothes", "Shoes", "Amazon Order", "Electronics", "Home Decor"],
            'Entertainment': ["Movie Tickets", "Concert", "Gaming", "Streaming Subscription", "Theme Park"],
            'Health': ["Pharmacy", "Doctor Consultation", "Vitamins", "Lab Test", "Gym Membership"]
        }
        
        new_expenses = []
        
        # Ensure at least 3 per category per month to get well over 25 total
        for month_label, m_start, m_end in months:
            for cat_name, cat_obj in categories.items():
                # Random 3 to 5 expenses per category per month
                num_expenses = random.randint(3, 5)
                for _ in range(num_expenses):
                    min_amt, max_amt = category_amount_ranges[cat_name]
                    amount = round(random.uniform(min_amt, max_amt), 2)
                    desc = random.choice(descriptions[cat_name])
                    e_date = generate_random_date(m_start, m_end)
                    
                    new_expenses.append(
                        Expense(
                            user_id=user.id,
                            category_id=cat_obj.id,
                            description=desc,
                            amount=amount,
                            date=e_date,
                            predicted_category=cat_name, # Also set predicted for completeness
                            confidence=0.99
                        )
                    )
                    
        db.session.add_all(new_expenses)
        db.session.commit()
        
        print(f"\nInserted {len(new_expenses)} new expenses successfully!\n")
        
        # Aggregate and print summary table
        summary = defaultdict(lambda: defaultdict(lambda: {"count": 0, "total": 0.0}))
        
        for exp in new_expenses:
            # Determine which month bucket it falls into
            if month_before_start <= exp.date <= month_before_end:
                m_label = "Month Before"
            elif last_month_start <= exp.date <= last_month_end:
                m_label = "Last Month"
            else:
                m_label = "This Month"
                
            cat_name = exp.category.name if exp.category else exp.predicted_category
            summary[m_label][cat_name]["count"] += 1
            summary[m_label][cat_name]["total"] += exp.amount
            
        print("=" * 70)
        print(f"{'Month':<15} | {'Category':<15} | {'Count':<7} | {'Total Amount (INR)'}")
        print("-" * 70)
        
        for month_label, _, _ in months:
            if month_label in summary:
                # Calculate month total for the sub-footer
                month_total = sum(d["total"] for d in summary[month_label].values())
                
                for cat_name in category_names:
                    if cat_name in summary[month_label]:
                        data = summary[month_label][cat_name]
                        print(f"{month_label:<15} | {cat_name:<15} | {data['count']:<7} | INR {data['total']:.2f}")
                
                print(f"{'':<15} | {'---':<15} | {'---':<7} | Month Total: INR {month_total:.2f}")
                print("-" * 70)

if __name__ == "__main__":
    seed_data()
