"""
Create a request to MonkeyLearn's hotel aspect detection and sentiment services and record results.
Aspect detection: https://app.monkeylearn.com/main/classifiers/cl_TKb7XmdG/
Sentiment analysis: https://app.monkeylearn.com/main/classifiers/cl_LD3be9HJ/

Example of running this script:
    python review_sentiment -token 123456789asdf

"""
import argparse
import json

import requests

import pandas as pd
import sys


def prepare_parser():
    """ Parse the command line arguments.

    Arguments:
        --input: Name of the input file, defaults to 'input.txt'.
        --output: Name of the output file, defaults to 'output.txt'.
        --token: MonkeyLearn authorization token.
        --aspect_id: MonkeyLearn aspect classifier ID, defaults to official classifier.
        --sentiment_id: MonkeyLearn sentiment classifier ID, defaults to official classifier.
    Returns:
        The parser with all the arguments.
    """

    parser = argparse.ArgumentParser(description='Run a MonkeyLearn sentiment analysis.')
    parser.add_argument('-i', '--input', default='input.txt', help='Name of the input file.')
    parser.add_argument('-o', '--output', default='output.txt', help='Name of the output file.')
    parser.add_argument('-t', '--token', required=True, help='MonkeyLean authorization token.')
    parser.add_argument(
        '-a', '--aspect_id', default='cl_TKb7XmdG', help='MonkeyLearn aspect classifier.')
    parser.add_argument(
        '-s', '--sentiment_id', default='cl_LD3be9HJ', help='MonkeyLearn sentiment classifier.')
    return parser


def prepare_data(filename):
    """ Read the file and convert the lines to a list of strings. """
    with open(filename, 'r') as f:
        if filename.lower().endswith('.csv'):
            pd.options.display.max_colwidth = 999
            data = pd.read_csv(filename, usecols=['review'])
            return map(str.strip, data.to_string(index=False, header=False, formatters=[str.strip, ]).splitlines())
        return f.read().splitlines()


def make_request(classifier_id, token, text_list):
    """ Make a request to a MonkeyLearn classifier.

    Arguments:
        classifier_id (str): The ID of the particular MonkeyLearn classifier.
        token (str): MonkeyLearn authorization token.
        text_list (list of strings): List of hotel reviews that is sent to the classifier.
    Returns:
        Response of the request
    Raises:
        Exception when the request response status is other than 200.
    """
    url = 'https://api.monkeylearn.com/v2/classifiers/{}/classify/'.format(classifier_id)
    data = {"text_list": text_list}
    auth = 'Token {}'.format(token)
    response = requests.post(url, data=data, headers={'Authorization': auth})
    if response.status_code != 200:
        exception_msg = 'Classifier "{}" returned status {} [{}]'.format(
            classifier_id, response.status_code, response.content
        )
        raise Exception(exception_msg)
    return response


def get_sentiments_from_csv(filename):
    """ Read CSV and return list of labeled sentiments as 1 for positive, 0 for negative """

    with open(filename, 'r') as f:
        pd.options.display.max_colwidth = 999
        data = pd.read_csv(filename, usecols=['sentiment'])
        sentiments = data.to_dict(orient='list')['sentiment']
        return sentiments


def get_sentiments_from_results(results):
    """ Filter sentiments from results and replace labels - 1 for Good (positive), 2 for Bad (negative) """
    sentiments = map(lambda x: 1 if x == 'Good' else 0, [result[0]['label'] for result in results])
    return sentiments


def compare_results(labeled_sentiments, sentiment_results):
    """ Compares sentiments labeled sentiments (i.e. from training set) with the ones returned from analysis. """
    matches = [1 if sentiment == result else 0 for sentiment, result in zip(labeled_sentiments, sentiment_results)]
    return matches


def main():
    """ Make requests to aspect and sentiment classifiers and save the results to output file.
        The format of the output file will be:
            review text, list of aspect pairs (probablity, label), sentiment pair (probabilty, label)
            ...
    """

    # Hack enables setting default encoding to UTF-8, without reloading setdefaultencoding() does not exist.
    reload(sys)
    sys.setdefaultencoding('utf8')

    parser = prepare_parser()
    args = parser.parse_args()
    text_list = prepare_data(args.input)
    aspect_response = make_request(args.aspect_id, args.token, text_list)
    sentiment_response = make_request(args.sentiment_id, args.token, text_list)
    aspect_result = json.loads(aspect_response.content)['result']
    sentiment_result = json.loads(sentiment_response.content)['result']
    results = zip(text_list, aspect_result, sentiment_result)

    with open(args.output, 'w') as f:
        for result in results:
            aspects = []
            for aspect in result[1]:
                aspects.append((aspect[0]['probability'], aspect[0]['label']))
            sentiment = (result[2][0]['probability'], result[2][0]['label'])
            f.write('{},{},{}\n'.format(result[0].encode('utf8'), aspects, sentiment))

    # If input data format is CSV compare labeled sentiments from CSV with results from analysis.
    if args.input.lower().endswith('.csv'):
        labeled_sentiments = get_sentiments_from_csv(args.input)
        labeled_results = get_sentiments_from_results(sentiment_result)
        matches = compare_results(labeled_sentiments, labeled_results)
        relative_matching = sum(matches) / float(len(matches))

        with open('matches.txt', 'w') as f:
            f.write('Matches by row (Labeled sentiment, Analysis result, Match):\n')
            for labeled_sentiment, labeled_result, match in zip(labeled_sentiments, labeled_results, matches):
                f.write('{}\t{}\t{}\n'.format(labeled_sentiment, labeled_result, match))
            f.write('\nRelative matching: {}\n'.format(relative_matching))


if __name__ == '__main__':
    main()
