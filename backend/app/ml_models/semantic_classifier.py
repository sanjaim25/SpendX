"""
Semantic embedding-based expense categorizer.

Uses sentence-transformers (all-MiniLM-L6-v2) to embed descriptions and
classify them by cosine similarity to precomputed category centroids.
"""

import os
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_THIS_DIR))), "data")
_TRAINING_CSV = os.path.join(_DATA_DIR, "training_data.csv")
_CENTROIDS_PATH = os.path.join(_THIS_DIR, "category_centroids.pkl")

# Confidence threshold: cosine similarity to averaged centroids compresses
# toward the middle of the range for short text.  0.30 is a good threshold
# based on evaluate_classifier.py and test examples.
CONFIDENCE_THRESHOLD = 0.30

# ---------------------------------------------------------------------------
# Singleton model loading — loaded once at import time, never per-request
# ---------------------------------------------------------------------------
_sentence_model = None


def _get_model():
    """Return the SentenceTransformer model, loading it once on first call."""
    global _sentence_model
    if _sentence_model is None:
        from sentence_transformers import SentenceTransformer
        _sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _sentence_model


# ---------------------------------------------------------------------------
# Centroid computation — pure function (no disk I/O)
# ---------------------------------------------------------------------------


def compute_centroids_from_dataframe(df: pd.DataFrame) -> tuple[list[str], np.ndarray]:
    """Compute one centroid embedding per category from a DataFrame.

    Args:
        df: DataFrame with columns ``description`` and ``category``.

    Returns:
        Tuple of (category_labels, centroids_array) where centroids_array has
        shape (n_categories, embedding_dim).
    """
    model = _get_model()
    categories = sorted(df["category"].unique())
    centroids = []

    for cat in categories:
        descriptions = df.loc[df["category"] == cat, "description"].tolist()
        if not descriptions:
            warnings.warn(
                f"Category '{cat}' has 0 examples — skipping centroid computation.",
                stacklevel=2,
            )
            continue
        embeddings = model.encode(descriptions, show_progress_bar=False)
        centroid = np.mean(embeddings, axis=0)
        centroids.append((cat, centroid))

    if not centroids:
        raise ValueError("No categories with examples found — cannot compute centroids.")

    labels = [c[0] for c in centroids]
    centroid_matrix = np.vstack([c[1] for c in centroids])
    return labels, centroid_matrix


# ---------------------------------------------------------------------------
# Centroid persistence
# ---------------------------------------------------------------------------
_category_labels: list[str] | None = None
_centroid_matrix: np.ndarray | None = None


def _load_or_build_centroids():
    """Load centroids from disk, or build + save them if missing."""
    global _category_labels, _centroid_matrix

    if _category_labels is not None and _centroid_matrix is not None:
        return

    if os.path.exists(_CENTROIDS_PATH):
        try:
            data = joblib.load(_CENTROIDS_PATH)
            _category_labels = data["labels"]
            _centroid_matrix = data["centroids"]
            return
        except Exception:
            warnings.warn(
                "category_centroids.pkl is corrupt — rebuilding from training data.",
                stacklevel=2,
            )

    retrain_centroids()


def retrain_centroids():
    """Re-read training_data.csv and recompute/save category centroids."""
    global _category_labels, _centroid_matrix

    if not os.path.exists(_TRAINING_CSV):
        raise FileNotFoundError(f"Training data not found at {_TRAINING_CSV}")

    df = pd.read_csv(_TRAINING_CSV)
    labels, centroids = compute_centroids_from_dataframe(df)

    joblib.dump({"labels": labels, "centroids": centroids}, _CENTROIDS_PATH)
    _category_labels = labels
    _centroid_matrix = centroids
    print(f"✅ Centroids saved to {_CENTROIDS_PATH} ({len(labels)} categories)")


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------


def predict_category_semantic(description: str) -> dict:
    """Predict expense category from description using semantic embeddings.

    Returns:
        dict with keys: ``category``, ``confidence`` (0-1), ``all_scores``
        (dict of category→similarity).
    """
    _load_or_build_centroids()

    text = (description or "").strip()
    if not text:
        return {
            "category": "Uncategorized",
            "confidence": 0.0,
            "all_scores": {},
        }

    model = _get_model()
    query_embedding = model.encode([text], show_progress_bar=False)
    similarities = cosine_similarity(query_embedding, _centroid_matrix)[0]

    all_scores = {
        label: round(float(sim), 4)
        for label, sim in zip(_category_labels, similarities)
    }

    best_idx = int(np.argmax(similarities))
    best_score = float(similarities[best_idx])
    best_category = _category_labels[best_idx]

    if best_score < CONFIDENCE_THRESHOLD:
        best_category = "Uncategorized"

    return {
        "category": best_category,
        "confidence": round(best_score, 4),
        "all_scores": all_scores,
    }


if __name__ == "__main__":
    retrain_centroids()
    test_cases = [
        "Swiggy order Rs 350",
        "Uber cab to airport",
        "Netflix monthly subscription",
        "Electricity bill payment",
        "Amazon shopping clothes",
        "Gym membership annual",
        "xyzzy foobar blargh",
    ]
    for desc in test_cases:
        result = predict_category_semantic(desc)
        print(f"  {desc:40s} → {result['category']:16s} ({result['confidence']:.3f})")
