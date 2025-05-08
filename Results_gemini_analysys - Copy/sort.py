import os
import csv

def process_csv_files(files_to_process):
    """
    Processes the specified CSV files to keep only the first and last columns,
    and saves the processed files.  Reads original files from the backup directory.

    Args:
        files_to_process (list): A list of filepaths to the CSV files to process.
    """
    # Define the backup directory
    backup_dir = "backup"

    for filename in files_to_process:
        # Construct the full path to the original file in the backup directory
        backup_file_path = os.path.join(backup_dir, filename)
        output_file_path = filename  # Output to the original filename

        try:
            # Open the original CSV file from the backup directory for reading
            with open(backup_file_path, 'r', encoding='utf-8') as infile:
                reader = csv.reader(infile)
                data = list(reader)  # Read all rows into a list

            # Check if the file is empty or has no rows
            if not data:
                print(f"Warning: {backup_file_path} is empty. Skipping.")
                continue

            # Get the first and last column index
            if len(data[0]) < 2:
                print(f"Warning: {backup_file_path} has less than two columns. Skipping.")
                continue
            first_column_index = 0
            last_column_index = len(data[0]) - 1

            # Prepare the data for the new CSV file
            new_data = []
            for row in data:
                new_row = [row[first_column_index], row[last_column_index]]
                new_data.append(new_row)

            # Write the new data to the CSV file, overwriting the original
            with open(output_file_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                writer.writerows(new_data)

            print(f"Processed file saved to {output_file_path}")

        except FileNotFoundError:
            print(f"Error: File not found at {backup_file_path}. Skipping.")
        except Exception as e:
            print(f"An error occurred while processing {backup_file_path}: {e}")
            print("Skipping this file.")

    print("File processing complete.")

if __name__ == "__main__":
    # List of CSV files to process.  These should be the *original* filenames.
    csv_files = [
        "gemini-2.0-flash_audio_analysis.csv",
        "gemini-2.0-flash_new_prompt_audio_analysis.csv",
        "gemini-2.0-flash-lite_audio_analysis.csv",
        "gemini-2.0-flash-lite_new_prompt_audio_analysis.csv",
    ]

    # Process the CSV files
    process_csv_files(csv_files)
