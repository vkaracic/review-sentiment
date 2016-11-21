import collections

import pandas as pd


VOCABULARY_SIZE = 1000

def build_vocabulary(words):
    """
    Creates a dictionary with the first VOCABULARY_SIZE number of words in all
    the CSV file reviews.

    Args:
        words(list): List of all the words in all the reviews in the CSV file.
    Returns:
        A dictionary where the keys are the words and values their position number
        in the frequency order.
    """
    count = collections.Counter(words).most_common(VOCABULARY_SIZE - 1)
    dictionary = dict()
    for word, _ in count:
        dictionary[word] = len(dictionary) + 1
    return dictionary


def vectorize(dictionary, words):
    """
    Converts a list of words into a list of frequency position numbers.

    Args:
        dictionary(dict): Dictionary containing the words in the vocabulary together
            with their frequency position.
        words(list): List of words that are to be converted.
    Returns:
        A list of frequency position numbers in place of the actual words in the list.
    """
    data = list()
    for word in words:
        if word in dictionary:
            index = dictionary[word]
        else:
            index = 0
        data.append(index)
    return data


def clean_row(review):
    """
    Cleans out a review and converts to list of words.
    Currently only removes empty elements left after removing some punctuations.

    Args:
        review(str): The review in string format.
    Returns:
        List of words in the accepted review, cleaned.
    """
    return [word for word in review.split(' ') if word != '']


def main():
    # Read the CSV file
    csv = pd.read_csv('/home/vedran/Downloads/test.csv')

    # Convert all the strings that in 'review' column to lowercase
    # to avoid same words being saved more than once.
    reviews = csv['review'].str.lower()

    # Clean out all the reviews. In case more cleaning is needed just append
    # a regex key and replacement value to the dictionary.
    cleaned_reviews = reviews.replace({
        '[.,]+\r': '',  # If a dot or comma has a space in front then remove it,
        '[.,]': ' '     # all the other ones are replaced with a whitespace.
    }, regex=True)

    # Create a global list of all the words within the CSV,
    # and build a vocabulary from them.
    words = []
    for i, row in cleaned_reviews.iteritems():
        words.extend(clean_row(row))
    dictionary = build_vocabulary(words)

    # Exchange the each of the reviews with their vectorized representations,
    # and save the new values to a new CSV file.
    for i, row in cleaned_reviews.iteritems():
        csv.set_value(i, 'review', vectorize(dictionary, clean_row(row)))
    csv.to_csv('/home/vedran/Downloads/test2.csv')


if __name__=='__main__':
    main()
