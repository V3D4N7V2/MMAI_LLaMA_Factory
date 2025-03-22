import pandas as pd
import re
import glob
import os

def categorize_sds_score(score):
    if 20 <= score <= 44:
        return "normal"
    elif 45 <= score <= 59:
        return "mildly"
    elif 60 <= score <= 69:
        return "moderately"
    else:
        return "severely"

def extract_sds_category(text):
    if type(text) in [int, float]:
        return categorize_sds_score(int(text))
    # if not isinstance(text, str):
    #     return "unknown"
    # Search for all numbers (including decimals) in the text
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
    # Filter numbers to those within the SDS range (20 to 80)
    valid_numbers = [float(num) for num in numbers if 20 <= float(num) <= 80]
    if valid_numbers:
        # Use the last valid number found
        score = valid_numbers[-1]
        return categorize_sds_score(score)
    
    # If no valid number is found, search for keywords (case-insensitive)
    if re.search(r'\b(severely)\b', text, re.IGNORECASE):
        return "severely"
    elif re.search(r'\b(moderately)\b', text, re.IGNORECASE):
        return "moderately"
    elif re.search(r'\b(mildly)\b', text, re.IGNORECASE):
        return "mildly"
    elif re.search(r'\b(normal)\b', text, re.IGNORECASE):
        return "normal"
    else:
        return "unknown"

def process_csv(input_file, output_file):
    df = pd.read_csv(input_file, index_col=False)
    
    # Process expected column (assumed to be a numeric SDS score)
    df['expected_category'] = df['expected_sds'].apply(lambda x: categorize_sds_score(x))
    
    # Process response column: if it's a string, extract SDS score/category
    df['response_category'] = df['predicted_sds'].apply(lambda x: extract_sds_category(x))
    
    # Keep only necessary columns and rename them accordingly
    df = df[['instance_id', 'response_category', 'expected_category']]
    df.columns = ['instance_id', 'response', 'expected']
    
    # Save to new CSV
    df.to_csv(output_file, index=False)
    print(f"Processed {input_file} -> {output_file}")

# Process all CSV files in the current directory that don't already have '_processed' in their name
for csv_file in glob.glob("*.csv"):
    if not csv_file.endswith("_processed.csv") and csv_file.endswith("flash_audio.csv"):
        base, ext = os.path.splitext(csv_file)
        output_file = f"{base}_processed{ext}"
        try:
            process_csv(csv_file, output_file)
        # process_csv(csv_file, output_file)
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")


