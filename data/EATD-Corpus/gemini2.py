import os
import csv
import time
import pandas as pd
from google import genai
from dotenv import load_dotenv
from pydub import AudioSegment
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report
import pprint

# Sample CSV output:
# instance_id,response,expected,message
# t_sample1,Normal,Normal,Success
# v_sample2,Mildly Depressed,Moderately Depressed,Success

# Sample Metrics Output:
# Evaluation Metrics for results_gemini_2.0_flash_audio_20250323-153000.csv:
# Precision: 0.85
# Recall: 0.80
# F1 Score: 0.82
#
# Classification Report:
#                  precision    recall  f1-score   support
# Below Normal         1.00      1.00      1.00         2
# Normal               0.90      0.80      0.85        10
# Mildly Depressed     0.75      0.70      0.72         5
# Moderately Depressed 0.60      0.70      0.65         3
# Severely Depressed   0.50      0.50      0.50         1

# Load environment variables (ensure your .env file contains GOOGLE_API_KEY=your_api_key)
load_dotenv()

# Instantiate the Google GenAI client
client = genai.Client(
    # api_key=os.getenv("GOOGLE_API_KEY"),
    api_key="AIzaSyBwv1S1Z8PR9CABnSYs2qPwFzFqJGPP5uU",
    http_options={"api_version": "v1alpha"}
)

def load_text_file(filepath):
    """Read a text file and return its stripped content."""
    with open(filepath, 'r', encoding="utf-8") as f:
        return f.read().strip()

def load_audio(filepath):
    """
    Read an audio file (WAV format) and return its binary content.
    Gemini accepts raw binary data for audio inputs.
    """
    with open(filepath, 'rb') as f:
        return f.read()

def sds_category(score):
    """
    Map a numeric SDS score to its category.
    If the score cannot be converted to a float, return the score as-is.
    """
    try:
        score = float(score)
    except Exception:
        return score
    if score < 20:
        return "Below Normal"
    elif 20 <= score <= 44:
        return "Normaly Depressed"
    elif 45 <= score <= 59:
        return "Mildly Depressed"
    elif 60 <= score <= 69:
        return "Moderately Depressed"
    else:  # score >= 70
        return "Severely Depressed"

def process_directory(directory, is_test=False):
    """
    Process a directory if its name matches the test/training prefix.
    
    For training, directories should start with 't_'; for testing, 'v_'.
    It reads transcription texts and audio files, builds a multimodal prompt,
    and calls the Gemini API to predict the SDS score.
    
    Returns a dictionary with keys:
      - instance_id: the directory name
      - response: predicted SDS category (or "error" on failure)
      - expected: SDS category from new_label.txt
      - message: "Success" or an error message
    """
    # Filter directories based on prefix
    if is_test and not directory.startswith('v_'):
        return None
    if not is_test and not directory.startswith('t_'):
        return None

    print("Processing directory:", directory)

    # Construct file paths
    negative_txt = os.path.join(directory, 'negative.txt')
    positive_txt = os.path.join(directory, 'positive.txt')
    neutral_txt  = os.path.join(directory, 'neutral.txt')
    negative_audio_path = os.path.join(directory, 'negative_out.wav')
    positive_audio_path = os.path.join(directory, 'positive_out.wav')
    neutral_audio_path  = os.path.join(directory, 'neutral_out.wav')
    expected_sds_path   = os.path.join(directory, 'new_label.txt')
    
    # Read text contents
    negative_text = load_text_file(negative_txt)
    positive_text = load_text_file(positive_txt)
    neutral_text  = load_text_file(neutral_txt)
    expected_sds  = load_text_file(expected_sds_path)
    
    # Build the user prompt text using transcriptions
    user_text = (
        f"Negative transcription: {negative_text}\n"
        f"Positive transcription: {positive_text}\n"
        f"Neutral transcription: {neutral_text}\n"
    )
    
    # Load audio files and combine them (if desired)
    negative_audio_segment = AudioSegment.from_file(negative_audio_path, format="wav")
    positive_audio_segment = AudioSegment.from_file(positive_audio_path, format="wav")
    neutral_audio_segment  = AudioSegment.from_file(neutral_audio_path, format="wav")
    
    combined_audio_segment = negative_audio_segment + positive_audio_segment + neutral_audio_segment
    combined_audio_segment.export("combined.wav", format="wav")
    combined_audio_binary = load_audio("combined.wav")

    # Define system instruction prompt for the model
    system_prompt = (
        "You are a therapist. I will provide you with 3 audio recording transcripts. "
        "Analyze the audios and transcripts to predict the sentiments in each audio. "
        "Based on the audio responses, predict the SDS (Zung Self-Rating Depression Scale) score. "
        "The scale is as follows: 20-44 (Normal), 45-59 (Mild Depression), 60-69 (Moderate Depression), "
        "70+ (Severe Depression). Output the Level of Depression as either Normal, Mild, Moderate or Severe. "
        """
        Sample output format: 
        
        I have analyzed the audio files, the person is Happy in the first audio. Neutral in the second audio, and upset in the third audio. I would say that the person is mildly depressed.

        Therefore final output is: 
        
        Mildly Depressed
        """
    )

    # Upload audio files via the client (Gemini requires file uploads)
    neg_audio_file = client.files.upload(file=negative_audio_path)
    pos_audio_file = client.files.upload(file=positive_audio_path)
    neu_audio_file = client.files.upload(file=neutral_audio_path)

    # Build the list of contents for Gemini; prepend system and user prompt
    contents = [ system_prompt + user_text, neg_audio_file, pos_audio_file, neu_audio_file ]

    # Set the model ID (choose between production and experimental)
    model_id = "gemini-2.0-flash"
    
    # Retry loop for API call
    while True:
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=contents,
            )
            # predicted_sds = response.text.strip()

            # find the last occurance of Normal, Mildly, Moderately, or Severely in the response using regex in lower case

            import re
            pattern = r"(normal|mild|moderate|severe)"
            matches = re.findall(pattern, response.text.lower())

            if matches:
                predicted_sds = matches[-1].capitalize() + "ly Depressed"

            else:
                predicted_sds = "error"


            message = response.text.strip()
            print(f"Directory {directory} - Predicted SDS: {predicted_sds}")
            break
        except Exception as e:
            print(f"Error processing directory {directory}: {e}")
            predicted_sds = "error"
            message = f"Error: {e}"
            time.sleep(10)
            break

    # Convert raw scores to SDS categories (if applicable)
    response_category = sds_category(predicted_sds)
    expected_category = sds_category(expected_sds)

    pprint.pprint({
        "instance_id": directory,
        "response": response_category,
        "expected": expected_category,
        "message": message
    })

    # input()

    return {
        "instance_id": directory,
        "response": response_category,
        "expected": expected_category,
        "message": message
    }

def process_all_directories():
    """
    Processes all subdirectories (both training and test) and returns the results list.
    """
    # Change to the script's directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)
    
    # List all subdirectories in the current folder
    directories = [d for d in os.listdir('.') if os.path.isdir(d)]
    results = []
    
    # Process training and test directories
    for d in directories:
        # test if directory is v_
        if d.startswith('v_'):
            result = process_directory(d, is_test=True)
            if result is not None:
                results.append(result)
    return results

def save_results_csv(results, filename):
    """
    Saves the results (list of dictionaries) to a CSV file with the specified filename.
    CSV columns: instance_id, response, expected, message.
    Note: SDS scores are mapped to their categories before saving.
    """
    # Ensure that the results contain SDS categories by mapping them explicitly
    for row in results:
        row["response"] = sds_category(row["response"])
        row["expected"] = sds_category(row["expected"])
    
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["instance_id", "response", "expected", "message"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print("Results saved to", filename)

def calculate_metrics(csv_filename, model_template, model_hf_path, hash_value):
    """
    Reads the CSV file into a DataFrame, calculates evaluation metrics,
    prints a report, and saves the report to a text file.
    """
    output_df = pd.read_csv(csv_filename)
    
    # Extract true and predicted labels
    y_true = output_df["expected"]
    y_pred = output_df["response"]
    
    # Calculate evaluation metrics (using weighted average)
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    report = classification_report(y_true, y_pred, zero_division=0)
    
    # Build the output string for metrics
    output_str = f"Evaluation Metrics for {csv_filename}:\n"
    output_str += f"Precision: {precision:.2f}\n"
    output_str += f"Recall: {recall:.2f}\n"
    output_str += f"F1 Score: {f1:.2f}\n\n"
    output_str += "Classification Report:\n"
    output_str += report
    
    # Print the output to the console
    print(output_str)
    
    # Create a filename using the provided template components (replacing '/' with '_')
    results_filename = f"{model_template}_{model_hf_path}_{hash_value}_results.txt".replace("/", "_")
    
    # Save the output to the file
    with open(results_filename, "w") as f:
        f.write(output_str)
    
    print(f"\nMetrics saved to: {results_filename}")

def main():
    # Process directories and gather results
    results = process_all_directories()
    
    # Build a filename for the CSV output using a timestamp
    datetime_str = time.strftime("%Y%m%d-%H%M%S")
    csv_filename = f"results_gemini_2.0_flash_audio_{datetime_str}.csv"
    
    # Save the results to CSV with SDS categories only
    save_results_csv(results, csv_filename)
    
    # --- Define these variables as needed ---
    model_template = "my_model_template"
    model_hf_path = "my_model_hf_path"
    hash_value = "my_hash_value"
    # ------------------------------------------
    
    # Calculate metrics and save the evaluation report
    calculate_metrics(csv_filename, model_template, model_hf_path, hash_value)

if __name__ == "__main__":
    main()
