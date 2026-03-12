import pandas as pd
import numpy as np

from src.config import RAW_DATA_PATH, PROCESSED_DATA_PATH

def load_data(filepath: str) -> pd.DataFrame:
    """Load the raw drug interaction CSV file."""
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} interactions.")
    return df

def categorize_severity(description: str) -> str:
    """Determine severity based on keywords in the description."""
    if pd.isna(description):
        return 'Minor (Green)'
    
    desc_lower = str(description).lower()
    
    major_keywords = ['fatal', 'life-threatening', 'severe', 'toxicity']
    moderate_keywords = ['increase', 'decrease', 'metabolism', 'serum concentration']
    
    for kw in major_keywords:
        if kw in desc_lower:
            return 'Major (Red)'
            
    for kw in moderate_keywords:
        if kw in desc_lower:
            return 'Moderate (Yellow)'
            
    return 'Minor (Green)'

def preprocess_and_save():
    """Main preprocessing pipeline."""
    df = load_data(RAW_DATA_PATH)
    
    print("Categorizing severity...")
    # Apply category logic
    df['Severity'] = df['Interaction Description'].apply(categorize_severity)
    
    print("Severity distribution:")
    print(df['Severity'].value_counts())
    
    print(f"Saving processed data to {PROCESSED_DATA_PATH}...")
    df.to_pickle(PROCESSED_DATA_PATH)
    print("Data processing complete!")

if __name__ == "__main__":
    preprocess_and_save()
