import os
from openai import OpenAI
import pandas as pd
import time
import re

model="llama-3.3-70b-versatile"
model="deepseek-r1-distill-llama-70b" 
model="gpt-4o-mini"
# Initialize OpenAI client
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key='sk-yh3JsZ0grs4u3gFVHKxUU89RnlY2gduycX6CyWLTPeayIilT',
    base_url="https://api.chatanywhere.tech/v1"
    # base_url="https://api.chatanywhere.org/v1"
)
# )  # Make sure you have OPENAI_API_KEY in your environment variables

def get_sds_prediction(text):
    while True:
        try:
            print("Calling OpenAI API...")
            response = client.chat.completions.create(
                # model="gpt-3.5-turbo",
                # https://api.chatanywhere.tech/v1
                # model="gpt-4o-mini",
                model=model,
                messages=[
                    {"role": "system", "content": "You are a therapist. Analyze the given text and predict the SDS (Zung Self-Rating Depression Scale) score. The scale ranges from 20-44 (Normal), 45-59 (Mild Depression), 60-69 (Moderate Depression), and 70+ (Severe Depression). Return only the numerical score. Only the numerical score is required."},
                    {"role": "user", "content": text}
                ],
                temperature=0
            )
            break
            print(response)
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            # print(response)
            time.sleep(10)    
    return response.choices[0].message.content.strip()

def process_directories():
    results = []
    
    # Get all directories
    directories = [d for d in os.listdir('.') if os.path.isdir(d)]
    
    for directory in directories:
        print("Processing directory:", directory)
        # Skip files that are not directories
        if not os.path.isdir(directory):
            continue
            
        # Read text files
        negative_path = os.path.join(directory, 'negative.txt')
        positive_path = os.path.join(directory, 'positive.txt')
        neutral_path = os.path.join(directory, 'neutral.txt')
        expected_sds_path = os.path.join(directory, 'label.txt')
        expected_sds_new_path = os.path.join(directory, 'new_label.txt')
        
        try:
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
            
            combined_text =  "Negative Answer: " + negative + ' \nPositive Answer:' + positive + ' \n Neutral Answer:' + neutral
            
            # Get SDS prediction
            predicted_sds = get_sds_prediction(combined_text)
            
            # Store results
            results.append({
                'person_name': directory,
                'expected_SDS_Score': expected_sds,  # Replace with actual expected score
                'expected_SDS_Score_new': expected_sds_new,
                'SDS_score_predicted_by_API': re.findall(r'\d+', predicted_sds)[-1],
                'API_response': predicted_sds
            })
            print("Processed directory:", directory)
            
        except Exception as e:
            print(f"Error processing directory {directory}: {str(e)}")
        
    
    # Create and save CSV
    df = pd.DataFrame(results)
    df.to_csv(f'sds_results_{model}.csv', index=False)

if __name__ == "__main__":
    process_directories()
# ```
