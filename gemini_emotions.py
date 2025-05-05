import os
import time
from google import genai

# Initialize the Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Define the base directory containing your audio files
base_dir = "data/EATD-Corpus"

# Function to check if the output file already exists
def output_exists(file_path):
    output_filename = f"{os.path.splitext(file_path)[0]}.txt"
    return os.path.isfile(output_filename)

# Function to handle API rate limits with exponential backoff
def handle_rate_limit(attempt):
    backoff_time = 5  # Exponential backoff
    print(f"API rate limit reached. Retrying in {backoff_time} seconds...")
    time.sleep(backoff_time)

# Iterate over each subdirectory and file
for subdir in os.listdir(base_dir):
    subdir_path = os.path.join(base_dir, subdir)
    if os.path.isdir(subdir_path):
        for filename in os.listdir(subdir_path):
            if filename.endswith(".wav"):
                file_path = os.path.join(subdir_path, filename)
                
                # Skip if the output file already exists
                if output_exists(file_path):
                    print(f"Skipping {filename}: Output file already exists.")
                    # continue
                else:
                    # Upload the audio file
                    try:
                        audio_file = client.files.upload(file=file_path)
                    except Exception as e:
                        print(f"Error uploading {filename}: {e}")
                        continue
                    
                    # Infinite retry logic with exponential backoff
                    attempt = 0
                    while True:
                        try:
                            # Generate content with a concise prompt
                            response = client.models.generate_content(
                                model="gemini-2.0-flash",
                                contents=[f"Extract the emotion and sentiment from this audio clip. Respond with one word for each: <emotion> <sentiment>", audio_file]
                            )
                            
                            # Write the response to the text file
                            output_filename = f"{os.path.splitext(filename)[0]}.txt"
                            with open(output_filename, 'w') as f:
                                f.write(response.text.strip())
                            
                            print(f"Processed {filename}: {response.text.strip()} saved to {output_filename}")
                            break  # Exit the retry loop on success
                        except Exception as e:
                            print(f"Error processing {filename} (Attempt {attempt + 1}): {e}")
                            attempt += 1
                            handle_rate_limit(attempt)
