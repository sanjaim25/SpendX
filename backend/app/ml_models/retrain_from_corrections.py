import os
import pandas as pd
from app import create_app, db
from app.models import CategoryCorrection
from app.ml_models.semantic_classifier import retrain_centroids, _TRAINING_CSV

def retrain():
    app = create_app()
    with app.app_context():
        corrections = CategoryCorrection.query.order_by(CategoryCorrection.created_at.asc()).all()
        
        if not corrections:
            print("No category corrections found. Skipping retraining.")
            return

        print(f"Found {len(corrections)} corrections.")
        
        if not os.path.exists(_TRAINING_CSV):
            print(f"Error: Training data not found at {_TRAINING_CSV}")
            return
            
        df = pd.read_csv(_TRAINING_CSV)
        
        print("\nBefore merge category counts:")
        print(df['category'].value_counts())
        
        # Build dict from description to corrected_category, keeping the latest correction
        corrections_map = {}
        for c in corrections:
            corrections_map[c.description.strip()] = c.corrected_category
            
        print(f"\nUnique corrections to apply: {len(corrections_map)}")
        
        # Apply corrections to existing rows
        modified_count = 0
        for idx, row in df.iterrows():
            desc = str(row['description']).strip()
            if desc in corrections_map:
                if df.at[idx, 'category'] != corrections_map[desc]:
                    df.at[idx, 'category'] = corrections_map[desc]
                    modified_count += 1
                del corrections_map[desc]
                
        # Append new rows
        new_rows = []
        for desc, category in corrections_map.items():
            new_rows.append({"description": desc, "category": category})
            
        if new_rows:
            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
            
        print(f"Modified existing rows: {modified_count}")
        print(f"Appended new rows: {len(new_rows)}")
        
        print("\nAfter merge category counts:")
        counts = df['category'].value_counts()
        print(counts)
        
        # Check for zero examples
        zero_examples = [cat for cat in counts.index if counts[cat] == 0]
        if zero_examples:
            print(f"\nWARNING: The following categories have 0 examples after merge: {zero_examples}")
            print("To prevent centroid computation failure, skipping retrain. Please add manual examples to training_data.csv.")
            return
            
        df.to_csv(_TRAINING_CSV, index=False)
        print(f"\nSaved updated training data to {_TRAINING_CSV}")
        
        print("\nRetraining centroids...")
        retrain_centroids()
        
if __name__ == "__main__":
    retrain()
