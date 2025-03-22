import os
import csv
import time
import base64
import subprocess
from openai import OpenAI

# Instantiate the OpenAI client
client = OpenAI(
    api_key = 'sk-yh3JsZ0grs4u3gFVHKxUU89RnlY2gduycX6CyWLTPeayIilT', 
    base_url="https://api.chatanywhere.tech/v1",
    # base_url="https://api.chatanywhere.tech/v1",
)

def load_text_file(filepath):
    """Read a text file and return its contents as a stripped string."""
    with open(filepath, 'r', encoding="utf-8") as f:
        return f.read().strip()

def load_audio_base64(filepath):
    """Load an audio file and return its base64-encoded string."""
    with open(filepath, 'rb') as audio_file:
        return base64.b64encode(audio_file.read()).decode('utf-8')

def process_directory(directory, isTest=False):
    """
    Process one directory if it matches the test/training prefix.
    For training directories, names start with 't_', for test directories 'v_'.
    Reads text files and audio files, builds a prompt, and calls the GPT‑4o API.
    Returns a dict with the directory name, predicted SDS score, and expected SDS.
    """
    # Filter based on the directory name
    if isTest:
        if not directory.startswith('v_'):
            return None
    else:
        if not directory.startswith('t_'):
            return None

    print("Processing directory:", directory)
    # Construct full paths for text and audio files
    negative_txt = os.path.join(directory, 'negative.txt')
    positive_txt = os.path.join(directory, 'positive.txt')
    neutral_txt  = os.path.join(directory, 'neutral.txt')
    negative_audio_path = os.path.join(directory, 'negative_out.wav')
    positive_audio_path = os.path.join(directory, 'positive_out.wav')
    neutral_audio_path  = os.path.join(directory, 'neutral_out.wav')
    expected_sds_path = os.path.join(directory, 'label.txt')
    expected_sds_new_path = os.path.join(directory, 'new_label.txt')
    
    # Read transcription texts and expected SDS
    negative = load_text_file(negative_txt)
    positive = load_text_file(positive_txt)
    neutral  = load_text_file(neutral_txt)
    expected_sds = load_text_file(expected_sds_new_path)
    
    # Build a user prompt that includes the transcriptions
    user_text = (
        "Negative transcription: " + negative + "\n" +
        "Positive transcription: " + positive + "\n" +
        "Neutral transcription: " + neutral + "\n"
    )
    
    # System prompt instructs the model on its role and desired output
    system_prompt = (
        "You are a therapist. I will provide you with 3 audio recordings along with their transcriptions. "
        "Based on the audio responses, predict the SDS (Zung Self-Rating Depression Scale) score. "
        "The scale is as follows: 20-44 (Normal), 45-59 (Mild Depression), 60-69 (Moderate Depression), "
        "70+ (Severe Depression). Only output a number."
    )
    
    # Load the three audio files as base64 strings
    negative_audio_b64 = load_audio_base64(negative_audio_path)
    positive_audio_b64 = load_audio_base64(positive_audio_path)
    neutral_audio_b64  = load_audio_base64(neutral_audio_path)
    
    # Construct the messages in the style of the OpenAI Cookbook reference:
    messages = [
        {
            "role": "system", 
            "content": system_prompt
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_text},
                {"type": "input_audio", "input_audio": {"data": negative_audio_b64, "format": "wav"}},
                {"type": "input_audio", "input_audio": {"data": positive_audio_b64, "format": "wav"}},
                {"type": "input_audio", "input_audio": {"data": neutral_audio_b64, "format": "wav"}}
            ]
        }
    ]
    while True:
        try:
            # Call the GPT-4o audio preview API
            response = client.chat.completions.create(
                model="gpt-4o-audio-preview",
                modalities=["text"],  # As in the reference code
                messages=messages,
                temperature=0
            )
            predicted_sds = response.choices[0].message.content.strip()
            print(f"Directory {directory} - Predicted SDS: {predicted_sds}")
            break
        except Exception as e:
            print(f"Error processing directory {directory}: {e}")
            predicted_sds = "error"
            time.sleep(10)
    
    return {
        "directory": directory,
        "predicted_sds": predicted_sds,
        "expected_sds": expected_sds
    }

def main():
    # Change to the script's directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)
    
    # Gather all subdirectories
    directories = [d for d in os.listdir('.') if os.path.isdir(d)]
    results = []
    
    # Process training and test directories
    for d in directories:
        for flag in [False, True]:
            result = process_directory(d, isTest=flag)
            if result is not None:
                results.append(result)
    
    # Write the results to a CSV file named for the model
    output_filename = "results_gpt-4o-audio-preview.csv"
    with open(output_filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["directory", "predicted_sds", "expected_sds"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    
    print("Results saved to", output_filename)
    
    # Optionally, commit the changes using git
    # subprocess.run(["git", "add", "."])
    # subprocess.run(["git", "commit", "-m", "SDS predictions processed"])
    # subprocess.run(["git", "push"])

if __name__ == "__main__":
    main()
