import os
import json
import subprocess

script_dir = os.path.dirname(os.path.realpath(__file__))
cwd = os.getcwd()
# Change the current working directory to the script's directory
os.chdir(script_dir)

def process_directories(isTest=False):
    results = []
    
    # Get all directories
    directories = [d for d in os.listdir('.') if os.path.isdir(d)]
    
    for directory in directories:
        # if not directory.startswith('t_'): continue

        if isTest:
            if not directory.startswith('t_'): continue
        else:
            if not directory.startswith('v_'): continue


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
        user_prompt =  "Negative Answer: \nTranscription:" + negative + ' \nPositive Answer: \nTranscription:' + positive + ' \n Neutral Answer: \nTranscription:' + neutral
        # The user
        system_prompt = "You are a therapist. I will give you 3 audios, you will predict if the person in the audio is depressed or not. You will use the SDS (Zung Self-Rating Depression Scale) score. The scale ranges from 20-44 (Normal), 45-59 (Mild Depression), 60-69 (Moderate Depression), and 70+ (Severe Depression)."

        expected_prediction = expected_sds_new

        if not isTest:

            message_json = {
                "messages": [
                    # {"role": "user", "content": system_prompt},
                    {"role": "user", "content": system_prompt + user_prompt},
                    {"role": "assistant", "content": expected_prediction}
                ],
                # "audio": [negative_path_audio, positive_path_audio, neutral_path_audio]
                "audios": [f'EATD-Corpus/{directory}/negative_out.wav' , f'EATD-Corpus/{directory}/positive_out.wav' , f'EATD-Corpus/{directory}/neutral_out.wav']
                
            }

        if isTest:
            message_json = {
                "messages": [
                    # {"role": "user", "content": system_prompt},
                    {"role": "user", "content": system_prompt + user_prompt},
                    # {"role": "assistant", "content": expected_prediction}
                ],
                # "audio": [negative_path_audio, positive_path_audio, neutral_path_audio]
                "audios": [f'EATD-Corpus/{directory}/negative_out.wav' , f'EATD-Corpus/{directory}/positive_out.wav' , f'EATD-Corpus/{directory}/neutral_out.wav']
                
            }

        results.append(message_json)

        print("Processed directory:", directory)

        json.dump(results, open(f'{"test" if not isTest else "train"}_prompt.json', 'w', encoding="utf-8"), indent=4)

if __name__ == "__main__":
    process_directories(False)
    process_directories(True)
    print("Done")
    os.chdir(cwd)
    # git add . && git commit -m "test" && git push
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "test"])
    subprocess.run(["git", "push"])