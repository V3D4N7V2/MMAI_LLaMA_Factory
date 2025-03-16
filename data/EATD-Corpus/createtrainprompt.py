import os
import json

def process_directories():
    results = []
    
    # Get all directories
    directories = [d for d in os.listdir('.') if os.path.isdir(d)]
    
    for directory in directories:
        if not directory.startswith('t_'): continue
        print("Processing directory:", directory)
        # Skip files that are not directories
        if not os.path.isdir(directory):
            continue
            
        # Read text files
        negative_path = os.path.join(directory, 'negative.txt')
        positive_path = os.path.join(directory, 'positive.txt')
        neutral_path = os.path.join(directory, 'neutral.txt')
        #
        negative_path_audio = os.path.join(directory, 'negative_out.wav')
        positive_path_audio = os.path.join(directory, 'positive_out.wav')
        neutral_path_audio = os.path.join(directory, 'neutral_out.wav')
        #
        expected_sds_path = os.path.join(directory, 'label.txt')
        expected_sds_new_path = os.path.join(directory, 'new_label.txt')
        
        with open(negative_path, 'r', encoding="utf-8") as f:
            negative = f.read()
        with open(positive_path, 'r', encoding="utf-8") as f:
            positive = f.read()
        with open(neutral_path, 'r', encoding="utf-8") as f:
            neutral = f.read()
        with open(expected_sds_path, 'r', encoding="utf-8") as f:
            expected_sds = f.read()
        with open(expected_sds_new_path, 'r', encoding="utf-8") as f:
            expected_sds_new = f.read()
        
        user_prompt =  "Negative Answer: <audio> \nTranscription:" + negative + ' \nPositive Answer: <audio> \nTranscription:' + positive + ' \n Neutral Answer: <audio> \nTranscription:' + neutral

        system_prompt = "You are a therapist. The user will give you 3 audios, you will predict if the person in the audio is depressed or not. You will use the SDS (Zung Self-Rating Depression Scale) score. The scale ranges from 20-44 (Normal), 45-59 (Mild Depression), 60-69 (Moderate Depression), and 70+ (Severe Depression)."

        expected_prediction = expected_sds_new

        message_json = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": expected_prediction}
            ],
            "audio": [negative_path_audio, positive_path_audio, neutral_path_audio]
            
        }

        results.append(message_json)

        print("Processed directory:", directory)

        json.dump(results, open('train_prompt.json', 'w'), indent=4)

if __name__ == "__main__":
    process_directories()