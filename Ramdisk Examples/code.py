import pandas as pd

# Read the CSV file
df = pd.read_csv('train.csv')

# Select the fourth column
fourth_column = df.iloc[:, 3]

# Write the fourth column to a new CSV file
fourth_column.to_csv('fourth_column.csv', index=False)
