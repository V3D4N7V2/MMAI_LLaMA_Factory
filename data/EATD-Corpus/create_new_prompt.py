import os
import json
import subprocess
import time

script_dir = os.path.dirname(os.path.realpath(__file__))
cwd = os.getcwd()
os.chdir(script_dir)

from pydub import AudioSegment

def combine_wav_files_with_silence(file_paths, output_path, silence_duration_ms=1000):
    combined = AudioSegment.empty()
    silence = AudioSegment.silent(duration=silence_duration_ms)

    for file_path in file_paths:
        audio = AudioSegment.from_wav(file_path)
        combined += audio + silence

    combined.export(output_path, format='wav')

def sds_category(score):
    try:
        score = float(score)
    except:
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

def process_directories(isTest=False, has_audio=False):
    results = []
    directories = [d for d in os.listdir('.') if os.path.isdir(d)]
    
    for directory in directories:

        if isTest:
            if not directory.startswith('v_'): continue
        else:
            if not directory.startswith('t_'): continue


        print("Processing directory:", directory)
        if not os.path.isdir(directory):
            continue
            
        negative_path = os.path.join(directory, 'negative.txt')
        positive_path = os.path.join(directory, 'positive.txt')
        neutral_path = os.path.join(directory, 'neutral.txt')

        negative_path_audio = os.path.join(directory, 'negative_out.wav')
        positive_path_audio = os.path.join(directory, 'positive_out.wav')
        neutral_path_audio = os.path.join(directory, 'neutral_out.wav')

        combined_audio_path = os.path.join(directory, 'combined_out.wav')

        if not os.path.exists(combined_audio_path):
            combine_wav_files_with_silence([
                negative_path_audio, neutral_path_audio, positive_path_audio
            ], combined_audio_path)

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
        
        system_prompt = "You are a helpful Assistant. Do as the user instructs. Keep your answers short and concise."

        user_prompt =  f"Transcribe this audio: <audio>"
        
        if not has_audio: user_prompt = f"Transcribe this audio"
        
        expected_prediction = f"Clip 1: {negative} \nClip 2: {positive} \nClip 3: {neutral} \n"

        message_json = {
            "messages": [
                {"role": "user", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        if isTest:
            message_json['messages'].append({"role": "assistant", "content": expected_prediction})
            message_json['expected'] = expected_prediction
        
        if has_audio:
            message_json['audios'] = [f'EATD-Corpus/{directory}/combined_out.wav']

        message_json['directory'] = directory
        results.append(message_json)

        print("Processed directory:", directory)
        filename = ''
        if isTest:
            filename += 'test'
        else:
            filename += 'train'
        if has_audio:
            filename += '_audio'
        else:
            filename += '_no_audio'
        json.dump(results, open(f'{filename}_prompt.json', 'w', encoding="utf-8"), indent=4)
        # put in parent directory
        json.dump(results, open(os.path.join(f"{cwd}/data/", f'{filename}_prompt.json'), 'w', encoding="utf-8"), indent=4)

if __name__ == "__main__":
    process_directories(False)
    process_directories(True)
    process_directories(True, True)
    process_directories(False, True)
    print("Done")
    os.chdir(cwd)
    time.sleep(5)
    # git add . && git commit -m "test" && git push
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "test"])
    subprocess.run(["git", "push"])