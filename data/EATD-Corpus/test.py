import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report
import os
script_dir = os.path.dirname(os.path.realpath(__file__))
cwd = os.getcwd()
# Change the current working directory to the script's directory
os.chdir(script_dir)

# Function to map an SDS score to its category
def sds_category(score):
    # Note: Scores below 20 are not defined in the Zung scale,
    # so they could be flagged or treated as "Normal" if desired.
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
    # Load the CSV file. Replace 'your_file.csv' with your actual file path.
    csv_file = "corrected_sds_results_deepseek-r1-distill-llama-70b.csv"
    # csv_file = "sds_results_gpt-4o-mini.csv"
    df = pd.read_csv(csv_file)

    # Create a new column for the ground truth category using expected_SDS_Score_new
    df["true_category"] = df["expected_SDS_Score_new"].apply(sds_category)
    
    # Create a new column for the predicted category using SDS_score_predicted_by_API
    df["pred_category"] = df["SDS_score_predicted_by_API"].apply(sds_category)
    
    # Extract the true and predicted labels
    y_true = df["true_category"]
    y_pred = df["pred_category"]
    
    print("Results for:", csv_file)
    # Calculate precision, recall, and F1 score using weighted averaging.
    # The 'zero_division=0' parameter handles any potential division by zero.
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    # Print the metrics
    print("Precision: {:.2f}".format(precision))
    print("Recall: {:.2f}".format(recall))
    print("F1 Score: {:.2f}".format(f1))
    
    # Additionally, print a detailed classification report
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, zero_division=0))

if __name__ == "__main__":
    main()
