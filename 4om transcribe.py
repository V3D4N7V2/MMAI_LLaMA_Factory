import os
import time
import csv
import datetime
from openai import OpenAI  # Changed import

# Initialize the OpenAI client
# client = OpenAI(base_url="https://api.chatanywhere.tech/v1",api_key="sk-yh3JsZ0grs4u3gFVHKxUU89RnlY2gduycX6CyWLTPeayIilT", ) # Changed to OpenAI key
# model_name = "gpt-4o-mini"  # Or "gpt-3.5-turbo" or other suitable OpenAI model.  Important:  The gpt-4-turbo model can take a list of messages.
client = OpenAI(base_url="https://api.groq.com/openai/v1",
api_key="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", ) # Changed to OpenAI key
# api_key="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", ) # Changed to OpenAI key
# client = OpenAI(api_key="YOUR_OPENAI_API_KEY")
# Define the model to use (adjust as needed for OpenAI)
model_name = "llama-3.3-70b-versatile"  # Or "gpt-3.5-turbo" or other suitable OpenAI model.  Important:  The gpt-4-turbo model can take a list of messages.
# Directory containing the audio files
audio_dir = os.path.join(os.getcwd(), "data", "EATD-Corpus")
code_description = "audio_transcript"
# Questions for the experiment
questions = [
    "The transcript of the audio is: Negative: {0}, Positive: {1}, Neutral: {2}. What is the speaker's emotion?",
    "Based on the audio and the transcripts, what is the speaker's tone in each clip?",
    "Based on the audio and the past conversation, do you think the speaker is Normal, Mildly Depressed, Moderately Depressed, or Severely Depressed? Only output the answer.",
]

# Function to process one audio file using the OpenAI API
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

    # try: # Removed try-except block, kept the logic inside.
    if True:
        # Upload the audio and get a reference (OpenAI does *not* have a direct file upload for analysis in the same way)
        # audio_ref = client.files.upload(file=file_path) # Removed.  OpenAI uses a different approach. We'll send file path in the prompt.
        audio_ref = None

        # Construct messages for OpenAI.  Crucially different from Gemini.
        messages = [
            {"role": "system", "content": "You are an AI Mental Health assistant analyzing audio files."},
            #{"role": "user", "content": f"Analyze the following audio file: {audio_ref} and tell me the emotion and sentiment of the speaker. You can also provide additional insights or highlight important words."}, #Removed.  File path in prompt.
        ]
        #Get initial response
        try:
            r1 = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=200, #Added max_tokens
            )
            r1_text = r1.choices[0].message.content
            messages.append({"role": "assistant", "content": r1_text}) #add to messages
        except Exception as e:
            print(f"Error sending initial message: {e}")
            time.sleep(5)
            return None # Important: Return None on error to avoid further processing

        messages.append({"role": "user", "content": f"Analyze the following audio transcript and tell me the emotion and sentiment of the speaker. You can also provide additional insights or highlight important words."}) #Added.  File path in prompt.
        try:
            r2 = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=200, #Added max_tokens
            )
            r2_text = r2.choices[0].message.content
            messages.append({"role": "assistant", "content": r2_text})  # Add to messages
        except Exception as e:
            print(f"Error sending audio analysis request: {e}")
            time.sleep(5)
            return None  # Important: Return None on error

        answers = [r2_text] # changed from r2.text.strip()

        # Ask each question
        for q in questions:
            prompt = q.format(*transcripts)
            messages.append({"role": "user", "content": prompt}) #append user prompt
            while True:
                try:
                    # Send the question and get the response
                    resp = client.chat.completions.create(
                        model=model_name,
                        messages=messages, # Pass the accumulated messages
                        max_tokens=100,  #Added max_tokens
                    )
                    resp_text = resp.choices[0].message.content #changed
                    messages.append({"role": "assistant", "content": resp_text}) #append AI response.
                    break
                except Exception as e:
                    print(f"Error sending question: {e}")
                    time.sleep(5)
            answers.append(resp_text.strip())
        for i in range(0, len(answers)):
            answers[i] = answers[i].replace("\n", " ").replace("\r", " ")
        return answers
    # except Exception as e: #removed
    #     print(f"Error processing {file_path}: {e}")
    #     return None

# Main CSV logging routine
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"{model_name}_{code_description}.csv"

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
                # only proceed if djrectory name is t_ or v_
                print(parts[-1])
                # if not parts[-1].startswith("v_"):
                #     continue
                print(f"Processing {index} in {root}")
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
                # input("Press Enter to continue...")
                # exit()  # Break out of the file loop
