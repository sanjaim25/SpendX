import os
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

# Default training data (fallback if no CSV)
TRAINING_DATA = [
    ("swiggy order food delivery", "Food"),
    ("zomato biryani pizza burger", "Food"),
    ("grocery vegetables milk fruits", "Food"),
    ("restaurant dinner lunch breakfast", "Food"),
    ("uber cab taxi ride auto", "Transport"),
    ("ola ride petrol fuel diesel", "Transport"),
    ("metro bus train ticket travel", "Transport"),
    ("flight airways booking airfare", "Transport"),
    ("electricity bill payment monthly", "Bills"),
    ("internet broadband wifi recharge", "Bills"),
    ("mobile phone recharge prepaid postpaid", "Bills"),
    ("water gas utility bill", "Bills"),
    ("amazon flipkart online shopping clothes", "Shopping"),
    ("shoes dress kurta shirt purchase", "Shopping"),
    ("electronics mobile laptop gadget buy", "Shopping"),
    ("mall store fashion accessories", "Shopping"),
    ("netflix amazon prime subscription ott", "Entertainment"),
    ("movie theatre ticket cinema", "Entertainment"),
    ("spotify music concert event show", "Entertainment"),
    ("game gaming playstation xbox", "Entertainment"),
    ("hospital medicine doctor pharmacy", "Health"),
    ("gym fitness yoga health insurance", "Health"),
    ("medical dental appointment clinic", "Health"),
]


def train_model():
    """Train the Naive Bayes model and save it."""
    descriptions = [item[0] for item in TRAINING_DATA]
    labels = [item[1] for item in TRAINING_DATA]

    pipeline = Pipeline(
        [
            ("vectorizer", CountVectorizer(ngram_range=(1, 2))),
            ("classifier", MultinomialNB(alpha=1.0)),
        ]
    )
    pipeline.fit(descriptions, labels)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Naive Bayes model trained and saved to {MODEL_PATH}")
    return pipeline


def load_model():
    """Load the saved model or train a new one if missing/corrupt."""
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            print("Model file is invalid. Retraining model...")
            return train_model()

    print("Model not found. Training new model...")
    return train_model()


def predict_category(description: str) -> str:
    """Predict expense category from description."""
    model = load_model()
    prediction = model.predict([description.lower()])
    return prediction[0]


def predict_category_with_confidence(description: str) -> dict:
    """Return prediction with confidence probabilities."""
    model = load_model()
    desc = [description.lower()]
    prediction = model.predict(desc)[0]
    probabilities = model.predict_proba(desc)[0]
    classes = model.classes_

    confidence = {cls: round(float(prob), 4) for cls, prob in zip(classes, probabilities)}
    return {
        "category": prediction,
        "confidence": confidence,
        "top_category": prediction,
        "confidence_score": round(max(probabilities) * 100, 2),
    }


if __name__ == "__main__":
    train_model()
    print(predict_category_with_confidence("Swiggy order Rs 350"))
    print(predict_category_with_confidence("Uber cab to airport"))
    print(predict_category_with_confidence("Netflix subscription"))
