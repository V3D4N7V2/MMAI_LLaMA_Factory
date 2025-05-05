import csv
from collections import Counter

# Load emotion words into a set (lowercase for case-insensitive comparison)
with open('emotion_words_list.txt', 'r', encoding='utf-8') as f:
    emotion_words = set(line.strip().lower() for line in f if line.strip())

# Counter for all emotion word occurrences
emotion_word_counter = Counter()

# Counter for number of phrases containing at least one emotion word
phrases_with_emotion_word = 0

# Read phrases from the CSV
with open('fourth_column.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if not row:
            continue  # skip empty rows

        phrase = row[0].lower()  # Assuming phrases are in the first column
        words_in_phrase = phrase.split()

        # Count emotion word occurrences in this phrase
        word_counts = Counter(words_in_phrase)
        found_emotion_word = False

        for word in emotion_words:
            count = word_counts[word]
            if count > 0:
                emotion_word_counter[word] += count
                found_emotion_word = True

        if found_emotion_word:
            phrases_with_emotion_word += 1

# Output the results
print("Emotion Word Frequencies:")
for word, count in emotion_word_counter.items():
    print(f"{word}: {count}")

print(f"\nNumber of phrases containing at least one emotion word: {phrases_with_emotion_word}")
