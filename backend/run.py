from app import create_app
from app.ml_models.naive_bayes_model import load_model
import os

app = create_app()

if __name__ == "__main__":
    # Pre-load ML model on startup
    print("Loading ML model...")
    load_model()
    print("SmartSpend backend is starting...")
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("DEBUG", "True") == "True",
    )
