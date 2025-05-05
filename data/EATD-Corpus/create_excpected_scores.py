import pandas as pd

def calculate_sds_state(sds_score):
    """
    Categorizes depression state based on SDS score.

    Args:
        sds_score (float): The SDS score.

    Returns:
        str: The depression state category.
    """
    if 20 <= sds_score <= 44:
        return "Normal"
    elif 45 <= sds_score <= 59:
        return "Mildly Depressed"
    elif 60 <= sds_score <= 69:
        return "Moderately Depressed"
    elif sds_score >= 70:
        return "Severely Depressed"
    else:
        return "Invalid Score" # Added for scores outside the defined ranges

def process_sds_scores(csv_file):
    """
    Reads a CSV file, calculates new SDS scores, determines depression states,
    and writes the updated data back to the CSV file.

    Args:
        csv_file (str): The path to the CSV file.
    """
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file)

        # Calculate the new SDS scores
        df['expected_SDS_Score_new'] = df['expected_SDS_Score'] * 1.25

        # Determine the depression states based on original and new scores
        df['expected_state'] = df['expected_SDS_Score'].apply(calculate_sds_state)
        df['expected_state_new'] = df['expected_SDS_Score_new'].apply(calculate_sds_state)

        # Round the 'expected_SDS_Score_new' column to 2 decimal places
        df['expected_SDS_Score_new'] = df['expected_SDS_Score_new'].round(2)

        # Write the updated DataFrame back to the CSV file
        df.to_csv(csv_file, index=False)
        print(f"Successfully updated the CSV file: {csv_file}")

    except FileNotFoundError:
        print(f"Error: File not found at {csv_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Specify the path to your CSV file
    csv_file_path = "correct_labels.csv"  # Replace with the actual path to your CSV file
    process_sds_scores(csv_file_path)
