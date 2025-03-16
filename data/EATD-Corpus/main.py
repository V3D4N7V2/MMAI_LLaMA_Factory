# <think>
# Alright, the user has provided a task that involves reading text files from directories, sending the content to the OpenAI API, and then storing the results in a CSV file. Let me break down what needs to be done.

# First, I need to understand the directory structure. Each directory represents a person and contains three text files: negative.txt, positive.txt, and neutral.txt, along with a label.txt. The directories are named like t_9, t_<number>, v_<number>, etc.

# The goal is to read each of these text files, combine their content, and send it to the OpenAI API to get a score on the SDS scale. Then, store the results in a CSV with columns for person name, expected SDS score, and the predicted score from the API.

# So, the steps are:

# 1. Traverse each directory and read the text files.
# 2. Combine the content of negative, positive, and neutral files into one text.
# 3. Use OpenAI's API to analyze this text and get the SDS score.
# 4. Write the results into a CSV.

# I need to consider how to structure the code. Using Python makes sense because of its file handling capabilities and libraries like pandas for CSV operations.

# First, I'll import necessary modules: os for file handling, openai for API calls, and pandas for CSV.

# Next, I'll set up the OpenAI API key. The user should replace it with their actual key.

# Then, I'll create a list to hold the results for each person. Each entry will be a dictionary with the person's name, expected SDS, and predicted SDS.

# I'll write a function to get the SDS prediction by sending the combined text to the API. The function will return the score extracted from the response.

# The main part will loop through each directory. For each directory, I'll read the three text files, combine them, and call the API function. Then, I'll append the result to the list.

# Finally, I'll use pandas to create a DataFrame from the results list and save it to a CSV file.

# I should make sure to handle any potential errors, like files not found or API call failures, but for simplicity, I'll assume everything works as intended.

# I also need to note that the expected SDS score is hardcoded as 50 in the example, but the user should adjust this based on actual expected values, possibly by reading from label.txt if it's provided.

# So, putting it all together, the code will read the files, send to the API, and save to CSV as specified.
# </think>

# ```python
import os
from openai import OpenAI
import pandas as pd
import time
model="llama-3.3-70b-versatile"
model="deepseek-r1-distill-llama-70b" 

# Initialize OpenAI client
client = OpenAI(
    # api_key = 'sk-yh3JsZ0grs4u3gFVHKxUU89RnlY2gduycX6CyWLTPeayIilT', 
    # base_url="https://api.chatanywhere.tech/v1",
    # client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="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"
# )
)  # Make sure you have OPENAI_API_KEY in your environment variables

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
        expected_sds = os.path.join(directory, 'label.txt')
        expected_sds_new = os.path.join(directory, 'new_label.txt')
        
        try:
            with open(negative_path, 'r', encoding="utf-8") as f:
                negative = f.read()
            with open(positive_path, 'r', encoding="utf-8") as f:
                positive = f.read()
            with open(neutral_path, 'r', encoding="utf-8") as f:
                neutral = f.read()
            
            combined_text =  "Negative Answer: " + negative + ' \nPositive Answer:' + positive + ' \n Neutral Answer:' + neutral
            
            # Get SDS prediction
            predicted_sds = get_sds_prediction(combined_text)
            
            # Store results
            results.append({
                'person_name': directory,
                'expected_SDS_Score': expected_sds,  # Replace with actual expected score
                'expected_SDS_Score_new': expected_sds_new,
                'SDS_score_predicted_by_API': predicted_sds
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
