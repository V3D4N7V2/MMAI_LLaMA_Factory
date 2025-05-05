import os
import speechbrain as sb
import torchaudio

# Function to detect emotion from the audio file
def detect_emotion(audio_path):
    # Load the pre-trained emotion recognition model
    emotion_recognition = sb.pretrained.interfaces.Processor.from_hparams(source="speechbrain/emotion-recognition-voice", savedir="tmpdir")

    # Load the audio
    signal, sample_rate = torchaudio.load(audio_path)
    
    # Make the emotion prediction
    prediction = emotion_recognition.encode_batch(signal)

    # Convert the prediction to a label (assuming it is an index of emotions)
    predicted_emotion = prediction[0].item()
    return predicted_emotion

# Main function to process files in a specific folder structure
def process_files():
    # Get the current working directory
    current_directory = os.getcwd()

    # Define the base path for the EATD-Corpus
    base_path = os.path.join(current_directory, 'data', 'EATD-Corpus')

    # Find the directories that match the 'v_t' pattern
    for dir_name in os.listdir(base_path):
        # Check if the directory matches the v_t_<number> pattern
        if '_' in dir_name:
            v_t, number = dir_name.split('_')
            if v_t in ['v', 't'] and number.isdigit():
                # Loop through the emotions
                for emotion in ['negative', 'positive', 'neutral']:
                    # Construct the path to the audio file
                    audio_path = os.path.join(base_path, dir_name, emotion, f"{emotion}_out.wav")
                    
                    if os.path.exists(audio_path):
                        # Detect emotion from the audio
                        predicted_emotion = detect_emotion(audio_path)
                        
                        # Create the output file path
                        output_file = os.path.join(base_path, dir_name, emotion, f"detected_emotion_{emotion}_out.txt")
                        
                        # Write the detected emotion to the text file
                        with open(output_file, "w") as f:
                            f.write(f"Predicted Emotion: {predicted_emotion}\n")
                        
                        print(f"Processed {audio_path} - Detected Emotion: {predicted_emotion}")

# Run the processing function
if __name__ == "__main__":
    process_files()
