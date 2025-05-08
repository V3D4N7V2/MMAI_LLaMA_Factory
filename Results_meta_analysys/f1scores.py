import pandas as pd
from sklearn.metrics import f1_score, accuracy_score, recall_score, precision_score
import re

# Load the correct labels (ground truth)
try:
    correct_labels_df = pd.read_csv("correct_labels_cleaned.csv")
except FileNotFoundError:
    print("Error: correct_labels_cleaned.csv not found. Please make sure the file is in the same directory or provide the correct path.")
    exit()

# Define the files to analyze
file_list = [
    "llama-3.3-70b-versatile_new_prompt_no_audio_analysis.csv",
    "gpt-4o-mini_new_prompt_no_audio_analysis.csv"
]

# Define the possible depression states, all lowercased for comparison
possible_states = [
    "normal",
    "mild",
    "moderate",
    "severe",
]

def extract_person_name(filename):
    """
    Extracts the person_name from the filename.  Handles the case where the
    filename might or might not have "new_prompt" in it.  Assumes the
    filename format is generally "gemini-2.0-flash[-lite][_new_prompt]_audio_analysis.csv".
    """
    base_name = filename.replace("_audio_analysis.csv", "")
    parts = base_name.split("-")
    if "new_prompt" in parts:
        if "lite" in parts:
          return parts[3] # person name
        else:
          return parts[2]
    else:
        if "lite" in parts:
            return parts[2]
        else:
           return parts[1]

def find_best_match(prediction, possible_states):
    """
    Finds the best matching depression state in the list of possible states.
    This function handles cases where the prediction might contain extra words
    or have slightly different phrasing.
    """
    prediction = prediction.lower()
    for state in possible_states:
        if state in prediction:
            return state
    return "unknown"  # Return "unknown" if no match is found

def simplify_state(state):
    """Simplifies a depression state by removing 'ly depressed'."""
    state = state.lower()
    state = state.replace("ly depressed", "")
    state = state.replace("ly depressed", "")  # Make it idempotent
    return state.strip()


# Iterate through each file
for file_name in file_list:
    try:
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        print(f"Error: {file_name} not found. Skipping this file.")
        continue

    # Extract the person name.
    person_name = extract_person_name(file_name)


    # Iterate through the two label types
    for label_type in ["original", "new"]:
        # Create empty lists to store the true and predicted labels.
        true_labels = []
        predicted_labels = []

        # Iterate through each row in the file's DataFrame.
        for index, row in df.iterrows():
            # Get the person_name from the current row.
            file_person_name = row["Index"]

            # Find the corresponding row in the correct labels DataFrame.
            correct_label_row = correct_labels_df[correct_labels_df["person_name"] == file_person_name]

            if correct_label_row.empty:
                print(
                    f"Warning: No matching label found for {file_person_name} in correct_labels_cleaned.csv. Skipping."
                )
                continue  # Skip to the next row in the loop

            # Get the correct label from the correct labels DataFrame.
            if label_type == "original":
                true_label = correct_label_row.iloc[0]["expected_state"]
            else:
                true_label = correct_label_row.iloc[0]["expected_state_new"]

            # Get the predicted label from the current row.
            predicted_label = str(row["Q3"])  # Convert to string to handle potential non-string values

            # Find the best matching depression state.
            predicted_label = find_best_match(predicted_label, possible_states)
            true_label = true_label.lower()

            # Simplify the states before comparison
            true_label = simplify_state(true_label)
            predicted_label = simplify_state(predicted_label)

            # Append the true and predicted labels to the lists.
            true_labels.append(true_label)
            predicted_labels.append(predicted_label)

        # Check if there are any labels to calculate metrics.
        if not true_labels:
            print(
                f"No matching labels found for {file_name} and label type {label_type}. Skipping metric calculation."
            )
            continue

        # Calculate the metrics.
        f1 = f1_score(true_labels, predicted_labels, average="weighted")
        accuracy = accuracy_score(true_labels, predicted_labels)
        recall = recall_score(true_labels, predicted_labels, average="weighted")
        precision = precision_score(true_labels, predicted_labels, average="weighted")

        # Print the metrics for the current file.
        print(f"Metrics for {file_name} - {label_type} labels:")
        print(f"F1 Score: {f1:.4f}")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"Precision: {precision:.4f}")
        print("-" * 30)
