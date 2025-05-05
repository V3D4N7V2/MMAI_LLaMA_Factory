import os
import time
import csv
import datetime
from google import genai

# Initialize the Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# Define the model to use
model_name = "gemini-2.0-flash"
# Directory containing the audio files
audio_dir = "/data/EATD_Corpus/"

# Questions for the experiment
questions = [
    "The transcript of the audio is: Negative: {0}, Positive: {1}, Neutral: {2}. What is the speaker's emotion?",
    "Based on the audio and the transcripts, what is the speaker's tone in each clip?",
    "Based on the audio and the past conversation, do you think the speaker is Normal, Mildly Depressed, Moderately Depressed, or Severely Depressed?",
]

# Function to process one audio file using the chats API
def process_audio_file(file_path):
    # Read transcripts if available
    emotions = ["negative", "positive", "neutral"]
    transcripts = []
    for emo in emotions:
        txt_path = file_path.replace("combined_out.wav", f"{emo}.txt")
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                transcripts.append(f.read().strip())
        else:
            transcripts.append("")

    try:
        # Upload the audio and get a reference
        audio_ref = client.files.upload(file=file_path)

        # Create a new chat session for this file
        chat = client.chats.create(model=model_name)

        # System prompt
        chat.send_message("You are an AI Mental Health assistant analyzing audio files.")
        # Send audio reference and analysis prompt
        chat.send_message(audio_ref)
        chat.send_message(
            "Analyze the following audio file and tell me the emotion and sentiment of the speaker. "
            "You can also provide additional insights or highlight important words."
        )
        init_response = chat.send_message("Please provide your analysis.")
        answers = [init_response.text.strip()]

        # Ask each question
        for q in questions:
            prompt = q.format(*transcripts)
            resp = chat.send_message(prompt)
            answers.append(resp.text.strip())

        return answers
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Main CSV logging routine
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"audio_analysis_{timestamp}.csv"

# Determine already processed indices if file exists
processed_indices = set()
if os.path.exists(csv_filename):
    with open(csv_filename, mode='r', newline='', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)  # skip header
        for row in reader:
            if row:
                processed_indices.add(row[0])

# Open CSV in append or write mode
do_write_header = not os.path.exists(csv_filename)
with open(csv_filename, mode='a' if not do_write_header else 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    # Write header if new file
    if do_write_header:
        header = ["Index", "Overall Analysis"] + [f"Q{i+1}" for i in range(len(questions))]
        writer.writerow(header)

    # Walk directory
    for root, _, files in os.walk(audio_dir):
        for fname in files:
            if fname.endswith("combined_out.wav"):
                parts = root.split(os.sep)
                index = parts[-1]  # use the directory name (e.g., t_123 or v_456) as the index
                if index in processed_indices:
                    print(f"Skipping already processed {index}")
                    continue

                full_path = os.path.join(root, fname)
                answers = process_audio_file(full_path)
                if answers:
                    writer.writerow([index] + answers)
                    print(f"Processed {index}: {answers}")
                else:
                    print(f"Failed to process {index}")
