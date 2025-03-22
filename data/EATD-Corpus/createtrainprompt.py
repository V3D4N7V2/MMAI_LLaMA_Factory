import os
import json
import subprocess
import time

script_dir = os.path.dirname(os.path.realpath(__file__))
cwd = os.getcwd()
# Change the current working directory to the script's directory
os.chdir(script_dir)

from pydub import AudioSegment

def combine_wav_files_with_silence(file_paths, output_path, silence_duration_ms=1000):
    # Create an empty AudioSegment
    combined = AudioSegment.empty()

    # Define silence segment
    silence = AudioSegment.silent(duration=silence_duration_ms)

    for file_path in file_paths:
        # Load the current audio file
        audio = AudioSegment.from_wav(file_path)
        # Append the audio and then the silence
        combined += audio + silence

    # Export the combined audio
    combined.export(output_path, format='wav')

# # Example usage
# wav_files = ['audio1.wav', 'audio2.wav', 'audio3.wav']
# output_file = 'combined_output.wav'
# combine_wav_files_with_silence(wav_files, output_file)

def sds_category(score):
    try:
        score = int(score)
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
    
    # Get all directories
    directories = [d for d in os.listdir('.') if os.path.isdir(d)]
    
    for directory in directories:
        # if not directory.startswith('t_'): continue

        if isTest:
            if not directory.startswith('v_'): continue
        else:
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

        combined_audio_path = os.path.join(directory, 'combined_out.wav')

        # combine files into one if not already done

        if not os.path.exists(combined_audio_path):
            combine_wav_files_with_silence([
                negative_path_audio, neutral_path_audio, positive_path_audio
            ], combined_audio_path)
            # , neutral_path_audio

        # Combine audio files into one

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
        
        # user_prompt =  "Negative Answer: <audio> \nTranscription:" + negative + ' \nPositive Answer: <audio> \nTranscription:' + positive # + ' \n Neutral Answer: <audio> \nTranscription:' + neutral
        # user_prompt =  "Negative Answer: <audio> \nTranscription:" + negative + ' \nPositive Answer: <audio> \nTranscription:' + positive + ' \n Neutral Answer Transcription:' + neutral

        user_prompt = f'Answer Audio: <audio> \nNegative Answer Transcription: {negative} \nPositive Answer Transcription: {positive} \nNeutral Answer Transcription: + {neutral}'

        if not has_audio: user_prompt = f'Negative Answer Transcription: {negative} \nPositive Answer Transcription: {positive} \nNeutral Answer Transcription: + {neutral}'
        # user_prompt =  "Negative Answer: \nTranscription:" + negative + ' \nPositive Answer: \nTranscription:' + positive + ' \n Neutral Answer: \nTranscription:' + neutral
        # The user
        system_prompt = "You are a therapist. I will give you an audio with 3 answers, you will predict if the person in the audio is depressed or not. You will use the SDS (Zung Self-Rating Depression Scale) score. The scale ranges from 20-44 (Normal), 45-59 (Mild Depression), 60-69 (Moderate Depression), and 70+ (Severe Depression)."

        specify_output = "Please specify the SDS score for the audio. The scale ranges from 20-44 (Normal), 45-59 (Mild Depression), 60-69 (Moderate Depression), and 70+ (Severe Depression). Only output a number. Do no explain your answer."

        expected_prediction = sds_category(expected_sds_new)

        if not isTest:

            message_json = {
                "messages": [
                    # {"role": "user", "content": system_prompt},
                    {"role": "user", "content": system_prompt + user_prompt},
                    {"role": "assistant", "content": expected_prediction}
                ],
                # "audio": [negative_path_audio, positive_path_audio, neutral_path_audio]
                # "audios": [f'EATD-Corpus/{directory}/negative_out.wav' 
                # , f'EATD-Corpus/{directory}/positive_out.wav' 
                # # , f'EATD-Corpus/{directory}/neutral_out.wav'
                # ]
                # "audios": [f'EATD-Corpus/{directory}/combined_out.wav']
            }
            if has_audio:
                # "audios": [f'EATD-Corpus/{directory}/combined_out.wav'],
                message_json['audios'] = [f'EATD-Corpus/{directory}/combined_out.wav']

        if isTest:
            message_json = {
                "messages": [
                    # {"role": "user", "content": system_prompt},
                    {"role": "user", "content": system_prompt + user_prompt + specify_output},
                    # {"role": "assistant", "content": expected_prediction}
                ],
                # "audio": [negative_path_audio, positive_path_audio, neutral_path_audio]
                # "audios": [f'EATD-Corpus/{directory}/negative_out.wav' 
                # , f'EATD-Corpus/{directory}/positive_out.wav' 
                # # , f'EATD-Corpus/{directory}/neutral_out.wav'
                # ],
                "expected": expected_prediction
            }
            if has_audio:
                # "audios": [f'EATD-Corpus/{directory}/combined_out.wav'],
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