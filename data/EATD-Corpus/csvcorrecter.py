import csv
import os
import re
# Define file paths
input_csv = "sds_results.csv"
input_csv = "sds_results_deepseek-r1-distill-llama-70b.csv"
output_csv = "corrected_sds_results_deepseek-r1-distill-llama-70b.csv"

def read_file_content(filepath):
    """Reads the first line of a file if it exists, otherwise returns an empty string."""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.readline().strip()  # Read the first line and remove newline characters
    return ""

# Process the CSV
with open(input_csv, 'r', encoding='utf-8') as infile, open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    header = next(reader)  # Read header
    writer.writerow(header)  # Write header to new file

    for row in reader:
        row[1] = read_file_content(row[1])  # Read content from expected_SDS_Score file
        row[2] = read_file_content(row[2])  # Read content from expected_SDS_Score_new file
        row[3] = re.findall(r'\d+', row[3])[-1]  # Read content from SDS_score_predicted_by_API file
        writer.writerow(row)

print(f"Corrected CSV saved as {output_csv}")
