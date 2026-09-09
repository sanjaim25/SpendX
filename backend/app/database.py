from app import db

def init_db(app):
    """Initialize the database and create all tables."""
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully.")

def drop_db(app):
    """Drop all tables — use with caution."""
    with app.app_context():
        db.drop_all()
        print("⚠️ All tables dropped.")

def reset_db(app):
    """Reset the database."""
    drop_db(app)
    init_db(app)
    print("🔄 Database reset complete.")
