import os
import csv
import time
from google import genai
from dotenv import load_dotenv
from pydub import AudioSegment


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

def process_directory(directory, isTest=False):
    """
    Process a directory if its name matches the test/training prefix.
    For training, directories should start with 't_'; for testing, 'v_'.
    Reads transcription texts and audio files, builds a multimodal prompt,
    and calls the Gemini API to predict the SDS score.
    """
    # Filter directories based on prefix
    if isTest:
        if not directory.startswith('v_'):
            return None
    else:
        if not directory.startswith('t_'):
            return None

    print("Processing directory:", directory)
    
    # Construct full paths for transcription and audio files
    negative_txt = os.path.join(directory, 'negative.txt')
    positive_txt = os.path.join(directory, 'positive.txt')
    neutral_txt  = os.path.join(directory, 'neutral.txt')
    negative_audio_path = os.path.join(directory, 'negative_out.wav')
    positive_audio_path = os.path.join(directory, 'positive_out.wav')
    neutral_audio_path  = os.path.join(directory, 'neutral_out.wav')
    expected_sds_new_path = os.path.join(directory, 'new_label.txt')
    
    # Read the transcription texts and expected SDS score
    negative = load_text_file(negative_txt)
    positive = load_text_file(positive_txt)
    neutral  = load_text_file(neutral_txt)
    expected_sds = load_text_file(expected_sds_new_path)
    
    # Build a user prompt that includes the transcriptions
    user_text = "Negative transcription: " + negative + "\n" + "Positive transcription: " + positive + "\n" + "Neutral transcription: " + neutral + "\n"
    
    # Load the three audio files as binary data
    negative_audio = load_audio(negative_audio_path)
    positive_audio = load_audio(positive_audio_path)
    neutral_audio  = load_audio(neutral_audio_path)
    
    negative_audio = AudioSegment.from_file(negative_audio_path, format="wav")
    positive_audio = AudioSegment.from_file(positive_audio_path, format="wav")
    neutral_audio = AudioSegment.from_file(neutral_audio_path, format="wav")

    combined_audio = negative_audio + positive_audio + neutral_audio

    combined_audio.export("combined.wav", format="wav")

    combined_audio = load_audio("combined.wav")

    # For Gemini, we build a list of contents.
    # The first element is the user text prompt.
    # Subsequent elements are dictionaries representing audio inputs.
    # contents = [
    #     user_text,
    #     {"type": "audio", "data": combined_audio, "format": "wav"},
    #     # {"type": "audio", "data": positive_audio, "format": "wav"},
    #     # {"type": "audio", "data": neutral_audio, "format": "wav"}
    # ]
    
    # Define a system instruction for the model similar to your original code.
    system_prompt = (
        "You are a therapist. I will provide you with 3 audio recording transcripts. Based on the audio responses, predict the SDS (Zung Self-Rating Depression Scale) score. The scale is as follows: 20-44 (Normal), 45-59 (Mild Depression), 60-69 (Moderate Depression), 70+ (Severe Depression). Output the Level of Depression as either Normal, Mild, Moderate or Severe. 
    )

    negative_audio = client.files.upload(file=negative_audio_path)
    positive_audio = client.files.upload(file=positive_audio_path)
    neutral_audio = client.files.upload(file=neutral_audio_path)

    
    
    contents = [ system_prompt + user_text, negative_audio, positive_audio, neutral_audio ]

    # Build a configuration dictionary that includes the system instruction and desired response modality.
    config = {
        "system_instruction": system_prompt,
        "response_modalities": ["TEXT"]
    }
    
    # Specify the model to use – you can choose between the experimental or GA versions.
    model_id = "gemini-2.0-flash"  # Alternatively, "gemini-2.0-flash-exp" for experimental
    
    # Loop to retry in case of errors (e.g. network issues)
    while True:
        try:
            # Call the Gemini API to generate content using the multimodal prompt
            response = client.models.generate_content(
                model=model_id,
                contents=contents,
                # config=config
            )
            predicted_sds = response.text.strip()
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
    
    # Gather all subdirectories in the current folder
    directories = [d for d in os.listdir('.') if os.path.isdir(d)]
    results = []
    
    # Process both training and test directories
    for d in directories:
        for flag in [False, True]:
            result = process_directory(d, isTest=flag)
            if result is not None:
                results.append(result)
    
    # Save results to a CSV file
    datetime_str = time.strftime("%Y%m%d-%H%M%S")
    output_filename = f"results_gemini_2.0_flash_audio{datetime_str}.csv"
    with open(output_filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["directory", "predicted_sds", "expected_sds"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    
    print("Results saved to", output_filename)

if __name__ == "__main__":
    main()
