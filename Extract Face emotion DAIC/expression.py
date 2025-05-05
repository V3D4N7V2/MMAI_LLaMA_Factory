import csv

def detect_facial_expressions(input_path, output_path):
    """
    Detects facial expressions based on AU values in a CSV file.
    AUs are considered present if their value > 0.
    """
    # Define emotion mappings based on AU presence
    emotion_rules = {
        'Happiness': ['AU06_r', 'AU12_r'],
        'Sadness': ['AU01_r', 'AU04_r', 'AU15_r'],
        'Anger': ['AU04_r', 'AU05_r', 'AU23_c'],
        'Fear': ['AU01_r', 'AU02_r', 'AU04_r', 'AU20_r', 'AU26_r'],
        'Surprise': ['AU01_r', 'AU02_r', 'AU05_r'],
        'Disgust': ['AU09_r', 'AU15_r'],
        'Contempt': ['AU14_r', 'AU12_c'],
        # 'Blink': ['AU45_c'],
        # 'Lip Compression': ['AU23_c', 'AU25_r'],
        # 'Jaw Drop': ['AU26_r'],
        # 'Nose Wrinkle': ['AU09_r'],
        # 'Brow Lower': ['AU04_r'],
        # 'Chin Raise': ['AU17_r'],
        # 'Lip Suck': ['AU28_c']
    }

    # Read input CSV
    with open(input_path, newline='') as infile:
        reader = csv.reader(infile)
        headers = next(reader)  # First row is headers
        results = []

        for row in reader:
            frame = row[0]
            timestamp = row[1]

            # Map header names to values
            au_data = {header.strip(): float(val) for header, val in zip(headers, row)}
            # print(au_data)  # Debugging line to check AU data
            # input("Press Enter to continue...")  # Pause for debugging
            detected_expressions = []
            # has_list = []
            # print(au_data)  # Debugging line to check AU data
            for expr, au_list in emotion_rules.items():
                # for au in au_list:
                #     print("keys ",au_data.keys())  # Debugging line to check AU names
                #     print(au, au_data[au])  # Debugging line to check AU names
                #     print(au, au_data.get(au, 0))  # Debugging line to check AU values
                #     if au_data.get(au, 0) > 0:
                #         has_list.append(au)
                # print(frame, has_list)
                # input("Press Enter to continue...")  # Pause for debugging
                if all(au_data.get(au, 0) > 0 for au in au_list):
                    detected_expressions.append(expr)

            results.append({
                'frame': frame,
                'timestamp': timestamp,
                'expressions': ', '.join(detected_expressions) if detected_expressions else 'None'
            })

    # Write output CSV
    with open(output_path, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['frame', 'timestamp', 'expressions'])
        for result in results:
            writer.writerow([result['frame'], result['timestamp'], result['expressions']])

# Example usage
input_path = '300_CLNF_AUs.txt'  # Your input file
output_path = 'output_expressions.csv'  # Output file
detect_facial_expressions(input_path, output_path)

# import pandas as pd

# def detect_facial_expressions(df):
#     """
#     Detects facial expressions based on the presence of Action Units (AUs).
#     AUs are considered present if their value is > 0.
#     """
#     # Define emotion mappings based on AU presence
#     emotion_rules = {
#         'Happiness': ['AU06_r', 'AU12_r'],
#         'Sadness': ['AU01_r', 'AU04_r', 'AU15_r'],
#         'Anger': ['AU04_r', 'AU05_r', 'AU23_c'],
#         'Fear': ['AU01_r', 'AU02_r', 'AU04_r', 'AU20_r', 'AU26_r'],
#         'Surprise': ['AU01_r', 'AU02_r', 'AU05_r'],
#         'Disgust': ['AU09_r', 'AU15_r'],
#         'Contempt': ['AU14_r', 'AU12_c'],
#         'Blink': ['AU45_c'],
#         'Lip Compression': ['AU23_c', 'AU25_r'],
#         'Jaw Drop': ['AU26_r'],
#         'Nose Wrinkle': ['AU09_r'],
#         'Brow Lower': ['AU04_r'],
#         'Chin Raise': ['AU17_r'],
#         'Lip Suck': ['AU28_c']
#     }

#     results = []

#     for _, row in df.iterrows():
#         detected_expressions = []

#         for expr, au_list in emotion_rules.items():
#             print(row.keys())
#             print(row)
#             for au in au_list:
#                 print(au)
#                 print(au, row[au])
#             input("Press Enter to continue...")  # Pause for debugging
#             if all(float(row[au]) > 0.5 for au in au_list if au in df.columns):
#                 print(f"Detected {expr} for frame {row['frame']} with AUs: {au_list}")
#                 detected_expressions.append(expr)

#         results.append({
#             'frame': row['frame'],
#             # 'timestamp': row['timestamp'],
#             'expressions': ', '.join(detected_expressions) if detected_expressions else 'None'
#         })
#         return pd.DataFrame(results)

#     return pd.DataFrame(results)

# # Read the CSV file
# input_path = '300_CLNF_AUs.txt'  # Replace with your file path
# df_input = pd.read_csv(input_path ,  delimiter = ",", header = 0, encoding = 'utf-8')

# # Detect expressions
# output_df = detect_facial_expressions(df_input)

# # Display and save the results
# print(output_df)
# output_df.to_csv('output_expressions.csv', index=False)