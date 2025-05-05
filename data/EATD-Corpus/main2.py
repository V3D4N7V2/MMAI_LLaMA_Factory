import os
import csv
import time
import re
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from pydub import AudioSegment
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report
import pprint


base_urls = {
    "groq": "https://api.groq.com/openai/v1",
    "openai": "https://api.openai.com/v1"
    "gemini" "https://generativelanguage.googleapis.com/v1beta/openai/"
}



# Sample CSV output:
# instance_id,response,expected,message
# t_sample1,Normal,Normal,Success
# v_sample2,Mildly Depressed,Moderately Depressed,Success

# Sample Metrics Output:
# Evaluation Metrics for results_deepseek-r1-distill-llama-70b_20250323-153000.csv:
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

# Load environment variables (ensure your .env file contains OPENAI_API_KEY)
load_dotenv()

# --- Groq/OpenAI API Client Setup ---
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
)
# Select the model to use:
# Uncomment one of the following:
# model = "llama-3.3-70b-versatile"
model = "deepseek-r1-distill-llama-70b"

def load_text_file(filepath):
    """Read a text file and return its stripped content."""
    with open(filepath, 'r', encoding="utf-8") as f:
        return f.read().strip()

def load_audio(filepath):
    """
    Read an audio file (WAV format) and return its binary content.
    (Note: In this version the audio is combined with text but only the text is used in the API call.)
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
        return "Normal"
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
    and calls the Groq/OpenAI API to predict the SDS score.
    
    Returns a dictionary with keys:
      - instance_id: the directory name
      - response: predicted SDS category (or "error" on failure)
      - expected: SDS category from new_label.txt
      - message: full API response or error message
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
    
    # Read text files
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
    
    # Load and combine audio files (for completeness)  
    negative_audio_segment = AudioSegment.from_file(negative_audio_path, format="wav")
    positive_audio_segment = AudioSegment.from_file(positive_audio_path, format="wav")
    neutral_audio_segment  = AudioSegment.from_file(neutral_audio_path, format="wav")
    
    combined_audio_segment = negative_audio_segment + positive_audio_segment + neutral_audio_segment
    combined_audio_segment.export("combined.wav", format="wav")
    combined_audio_binary = load_audio("combined.wav")
    
    # Define system instruction prompt for the model (same as Gemini prompt)
    system_prompt = (
        "You are a therapist. I will provide you with 3 audio recording transcripts. "
        "Analyze the audios and transcripts to predict the sentiments in each audio. "
        "Based on the audio responses, predict the SDS (Zung Self-Rating Depression Scale) score. "
        "The scale is as follows: 20-44 (Normal), 45-59 (Mild Depression), 60-69 (Moderate Depression), "
        "70+ (Severe Depression). Output the Level of Depression as either Normal, Mild, Moderate or Severe.\n"
        """
        Sample output format: 
        
        I have analyzed the audio files, the person is Happy in the first audio. Neutral in the second audio, and upset in the third audio. I would say that the person is mildly depressed.
        
        Therefore final output is: 
        
        Mildly Depressed
        """
    )
    
    # Build combined prompt text (using both system prompt and user transcriptions)
    full_prompt = system_prompt + "\n" + user_text
    # (Note: The audio file is not sent to the API because the Groq/OpenAI endpoint currently accepts text only.)

    # Call the Groq/OpenAI API using chat completions
    while True:
        try:
            print("Calling Groq/OpenAI API...")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                temperature=0
            )
            # Obtain the API response text
            raw_response = response.choices[0].message.content.strip()
            # Use regex to extract a numerical score from the response if present
            match = re.search(r'\d+', raw_response)
            if match:
                predicted_sds_num = match.group()
            else:
                predicted_sds_num = "error"
            break
        except Exception as e:
            print(f"Error processing directory {directory}: {e}")
            predicted_sds_num = "error"
            raw_response = f"Error: {e}"
            time.sleep(10)
            break

    # Map numerical SDS score to SDS category
    response_category = sds_category(predicted_sds_num)
    expected_category = sds_category(expected_sds)

    pprint.pprint({
        "instance_id": directory,
        "response": response_category,
        "expected": expected_category,
        "message": raw_response
    })

    return {
        "instance_id": directory,
        "response": response_category,
        "expected": expected_category,
        "message": raw_response
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
    
    # Process directories: here we process only test directories starting with 'v_'
    for d in directories:
        result = process_directory(d, is_test=True)
        if result is not None:
            results.append(result)
    return results

def save_results_csv(results, filename):
    """
    Saves the results (list of dictionaries) to a CSV file with the specified filename.
    CSV columns: instance_id, response, expected, message.
    """
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
    
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    report = classification_report(y_true, y_pred, zero_division=0)
    
    output_str = f"Evaluation Metrics for {csv_filename}:\n"
    output_str += f"Precision: {precision:.2f}\n"
    output_str += f"Recall: {recall:.2f}\n"
    output_str += f"F1 Score: {f1:.2f}\n\n"
    output_str += "Classification Report:\n" + report
    
    print(output_str)
    
    results_filename = f"{model_template}_{model_hf_path}_{hash_value}_results.txt".replace("/", "_")
    with open(results_filename, "w") as f:
        f.write(output_str)
    
    print(f"\nMetrics saved to: {results_filename}")

def main():
    # Process directories and gather results
    results = process_all_directories()
    
    # Build a filename for the CSV output using a timestamp
    datetime_str = time.strftime("%Y%m%d-%H%M%S")
    csv_filename = f"results_{model}_{datetime_str}.csv"
    
    # Save results to CSV
    save_results_csv(results, csv_filename)
    
    # --- Define these variables as needed for metrics filename ---
    model_template = "my_model_template"
    model_hf_path = "my_model_hf_path"
    hash_value = "my_hash_value"
    # ---------------------------------------------------------------
    
    # Calculate evaluation metrics and save the report
    calculate_metrics(csv_filename, model_template, model_hf_path, hash_value)

if __name__ == "__main__":
    main()
