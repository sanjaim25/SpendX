import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np
from datetime import datetime

from app.ml_models.semantic_classifier import (
    compute_centroids_from_dataframe,
    _get_model,
    CONFIDENCE_THRESHOLD,
    _DATA_DIR,
    _TRAINING_CSV
)

# For monkey-patching semantic_classifier to use our in-memory centroids
import app.ml_models.semantic_classifier as sc

def evaluate():
    if not os.path.exists(_TRAINING_CSV):
        print(f"Training data not found at {_TRAINING_CSV}")
        return

    df = pd.read_csv(_TRAINING_CSV)
    
    # 80/20 stratified split
    train_df, test_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df['category']
    )
    
    print(f"Total samples: {len(df)}")
    print(f"Train samples: {len(train_df)}")
    print(f"Test samples: {len(test_df)}")
    
    # Check for duplicate leakages (exact match)
    train_descs = set(train_df['description'].str.lower().str.strip())
    test_descs = set(test_df['description'].str.lower().str.strip())
    leakage = train_descs.intersection(test_descs)
    if leakage:
        print(f"\nWARNING: {len(leakage)} test descriptions appear verbatim in training data!")
        print(f"Leakage examples: {list(leakage)[:5]}")
    else:
        print("\nNo verbatim string leakage detected between train and test sets.")
    
    # Compute centroids only on train split (in-memory)
    print("Computing centroids from training split...")
    labels, centroids = compute_centroids_from_dataframe(train_df)
    
    # Monkey-patch semantic_classifier so it doesn't try to load/save .pkl
    sc._category_labels = labels
    sc._centroid_matrix = centroids
    
    print("\nEvaluating on test split...")
    y_true = []
    y_pred_probs = []
    y_pred_cats = []
    
    for _, row in test_df.iterrows():
        desc = row['description']
        true_cat = row['category']
        
        result = sc.predict_category_semantic(desc)
        scores = result['all_scores']
        
        # Determine best prediction without applying threshold
        best_cat = max(scores, key=scores.get)
        best_score = scores[best_cat]
        
        y_true.append(true_cat)
        y_pred_probs.append(best_score)
        y_pred_cats.append(best_cat)
        
    print("\nThreshold Sweep Analysis:")
    print("Thresh | Accuracy | F1-Macro")
    print("----------------------------")
    for thresh in [0.20, 0.25, 0.30, 0.35, 0.40]:
        y_pred_thresh = [
            cat if score >= thresh else "Uncategorized" 
            for cat, score in zip(y_pred_cats, y_pred_probs)
        ]
        acc_t = accuracy_score(y_true, y_pred_thresh)
        f1_t = classification_report(y_true, y_pred_thresh, zero_division=0, output_dict=True)['macro avg']['f1-score']
        print(f" {thresh:.2f}  |  {acc_t:.4f}  |  {f1_t:.4f}")
        
    # Final metrics at configured threshold
    y_pred_final = [
        cat if score >= CONFIDENCE_THRESHOLD else "Uncategorized" 
        for cat, score in zip(y_pred_cats, y_pred_probs)
    ]
        
    acc = accuracy_score(y_true, y_pred_final)
    report = classification_report(y_true, y_pred_final, zero_division=0)
    cm = confusion_matrix(y_true, y_pred_final, labels=labels)
    
    print(f"\nAccuracy at threshold {CONFIDENCE_THRESHOLD}: {acc:.4f}\n")
    print("Classification Report:")
    print(report)
    print("Confusion Matrix:")
    
    # Print a nice plain text grid for CM
    print(f"{'':>15} " + " ".join([f"{l[:5]:>5}" for l in labels]))
    for i, row_label in enumerate(labels):
        row_str = " ".join([f"{val:5d}" for val in cm[i]])
        print(f"{row_label[:15]:>15} {row_str}")
        
    # Write to model_card.md
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(_DATA_DIR)), "backend", "docs")
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        
    model_card_path = os.path.join(docs_dir, "model_card.md")
    
    with open(model_card_path, "w", encoding="utf-8") as f:
        f.write("# Model Card: Semantic Expense Categorizer\n\n")
        f.write("- **Model**: all-MiniLM-L6-v2 sentence embeddings + cosine similarity to category centroids\n")
        f.write(f"- **Training data size**: {len(df)} examples across {len(labels)} categories\n")
        f.write(f"- **Test accuracy**: {acc * 100:.2f}%\n\n")
        f.write("### Per-category Performance\n")
        f.write("```text\n")
        f.write(report)
        f.write("\n```\n\n")
        f.write(f"- **Confidence threshold**: {CONFIDENCE_THRESHOLD} (below → Uncategorized)\n")
        f.write(f"- **Last evaluated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        
    print(f"\nModel card written to {model_card_path}")

if __name__ == "__main__":
    evaluate()
