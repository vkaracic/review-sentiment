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


def main():
    """ Make requests to aspect and sentiment classifiers and save the results to output file.
    The format of the output file will be:
        review text, list of aspect pairs (probablity, label), sentiment pair (probabilty, label)
        ...
    """
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
            f.write('{},{},{}\n'.format(result[0], aspects, sentiment))


if __name__ == '__main__':
    main()
