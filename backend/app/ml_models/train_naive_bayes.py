import pandas as pd
import os
import joblib
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '../../../data/training_data.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'model.pkl')


def train_from_csv():
    """Train model from CSV file."""
    if not os.path.exists(DATA_PATH):
        print(f"❌ CSV not found at {DATA_PATH}")
        return None

    df = pd.read_csv(DATA_PATH)

    # Validate required columns
    if 'description' not in df.columns or 'category' not in df.columns:
        print("❌ CSV must contain 'description' and 'category' columns.")
        return None

    print(f"📊 Loaded {len(df)} training samples")
    print(f"📂 Categories: {df['category'].unique()}")

    # Lowercase text
    df['description'] = df['description'].astype(str).str.lower()

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['description'],
        df['category'],
        test_size=0.2,
        random_state=42,
        stratify=df['category']
    )

    # Create pipeline
    pipeline = Pipeline([
        ('vectorizer', CountVectorizer(ngram_range=(1, 2), stop_words='english')),
        ('classifier', MultinomialNB(alpha=0.5))
    ])

    # Train
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print("\n📊 Model Performance")
    print("-" * 50)
    print(f"Accuracy: {accuracy * 100:.2f}%")
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    # Save model
    joblib.dump(pipeline, MODEL_PATH)
    print("\n✅ Model trained and saved successfully.")

    return pipeline


def evaluate_model(model):
    """Quick manual test cases."""
    if model is None:
        print("❌ Model not available for evaluation.")
        return

    test_cases = [
        ("Swiggy order biryani", "Food"),
        ("Uber cab ride", "Transport"),
        ("Netflix subscription", "Entertainment"),
        ("Electricity bill payment", "Bills"),
        ("Amazon shopping clothes", "Shopping"),
    ]

    print("\n🧪 Manual Test Evaluation")
    print("-" * 50)

    correct = 0

    for desc, expected in test_cases:
        predicted = model.predict([desc.lower()])[0]

        if predicted == expected:
            correct += 1

        print(f"{desc} → {predicted} (Expected: {expected})")

    print(f"\nManual Accuracy: {correct}/{len(test_cases)}")


if __name__ == '__main__':
    trained_model = train_from_csv()
    evaluate_model(trained_model)