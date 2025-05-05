import sys
import os
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report

def sds_category(score):
    """
    Map a numeric SDS score to its category.
    If the score cannot be converted to a float, assume it is already a category and return it.
    """
    try:
        score = float(score)
    except Exception:
        return score  # Assume score is already a category (e.g., "Mildly Depressed")
    if score < 20:
        return "Below Normal"
    elif 20 <= score <= 44:
        return "Normal"
    elif 45 <= score <= 59:
        return "Mildly Depressed"
    elif 60 <= score <= 69:
        return "Moderately Depressed"
    else:  # score >= 70
        return "Severely Depressed"

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <csv_file_path>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.isfile(csv_file):
        print(f"Error: File '{csv_file}' does not exist.")
        sys.exit(1)
    
    # Load the CSV file. Expected CSV columns: instance_id,response,expected,message
    df = pd.read_csv(csv_file)
    
    # Create new columns for true and predicted categories.
    # If the values are numeric, they will be mapped to categories. If not, they are used as-is.
    df["true_category"] = df["expected"].apply(sds_category)
    df["pred_category"] = df["response"].apply(sds_category)
    
    # Extract true and predicted labels
    y_true = df["true_category"]
    y_pred = df["pred_category"]
    
    print("Results for:", csv_file)
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    # Print metrics
    print("Precision: {:.2f}".format(precision))
    print("Recall: {:.2f}".format(recall))
    print("F1 Score: {:.2f}".format(f1))
    
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, zero_division=0))

if __name__ == "__main__":
    main()
