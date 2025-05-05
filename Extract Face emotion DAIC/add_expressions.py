import pandas as pd

# Read the transcript and expressions CSV files
transcript_df = pd.read_csv('300_transcript.csv', delimiter="\t")
expressions_df = pd.read_csv('output_expressions.csv', delimiter=",")

# Strip whitespace from column names
transcript_df.columns = transcript_df.columns.str.strip()
expressions_df.columns = expressions_df.columns.str.strip()

# Convert the timestamp and time range columns to float
transcript_df['start_time'] = transcript_df['start_time'].astype(float)
transcript_df['stop_time'] = transcript_df['stop_time'].astype(float)
expressions_df['timestamp'] = expressions_df['timestamp'].astype(float)

# Initialize the new column
transcript_df['face_emotion'] = None

# Loop through each row in the transcript to find relevant emotions
for index, row in transcript_df.iterrows():
    start = row['start_time']
    stop = row['stop_time']

    # Filter expressions within the time interval
    mask = (expressions_df['timestamp'] >= start) & (expressions_df['timestamp'] < stop)
    filtered = expressions_df[mask]

    # Extract emotions, handling comma-separated values, and use a set for uniqueness
    emotions_set = set()
    for expressions_str in filtered['expressions'].dropna():
        # Split the string by commas and add each emotion to the set
        for emotion in expressions_str.split(','):
            emotion = emotion.strip()  # Remove extra spaces
            if emotion != 'None':
                emotions_set.add(emotion)

    # Convert the set to a space-separated string
    emotions_string = ' '.join(emotions_set) if emotions_set else ''

    # Assign the space-separated string to the new column
    transcript_df.at[index, 'face_emotion'] = emotions_string

# Save the updated DataFrame to a new CSV file
transcript_df.to_csv('300_transcript_with_emotions.csv', index=False)
