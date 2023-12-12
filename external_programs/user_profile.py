import os
import csv


def clean_text(text):
    # Convert to lowercase and remove newlines
    text = text.lower().replace('\n', ' ')

    # Replace all symbols with spaces
    symbols = ['.', ',', '"', "'", '+', '(', ')', '/', '-', ':']
    for s in symbols:
        text = text.replace(s, ' ')

    # Remove all noise words
    noise_words = [' and ', ' or ', ' a ', ' an ', ' the ', ' your ', ' to ', ' which ', ' of ', ' is ', ' in ', ' on ']
    for n in noise_words:
        text = text.replace(n, ' ')

    # Substitute compound concepts
    text = text.replace(' first aid ', ' first_aid ')

    return text.strip()


def process_post(post_text, unique_words):
    cleaned_text = clean_text(post_text)
    words = cleaned_text.split()
    word_counts = {}
    for word in words:
        if word not in word_counts:
            word_counts[word] = 1
            unique_words.add(word)
        else:
            word_counts[word] += 1

    return word_counts

def create_user_profile_csv(favorite_posts, user_id):
    directory_path = "../user_profiles/"

    unique_words = set()
    word_counts = {}
    if favorite_posts:
        for post in favorite_posts:
            data = process_post(post[0], unique_words)
            for word, count in data.items():
                word_counts[word] = word_counts.get(word, 0) + count
            # print(data)

        # Calculate average word count
        for word in word_counts:
            word_counts[word] /= len(favorite_posts)

        # Write to CSV file
        csv_file_path = directory_path + 'user_profile_' + str(user_id) + '.csv'
        with open(csv_file_path, 'w', newline='') as csv_file:
            fieldnames = ['Word', 'Average']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Write header
            writer.writeheader()

            # Write data
            for word, count in word_counts.items():
                writer.writerow({'Word': word, 'Average': count})

        print(f'CSV file has been created: {csv_file_path}')