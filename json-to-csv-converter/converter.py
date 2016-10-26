"""
Example of running the script:
    python converter.py -i data_folder_with_json_files
"""

import argparse
import csv
import os

import json


def prepare_parser():
    """ Parse the command line arguments.

    Arguments:
        --input: Name of the input data folder, defaults to 'data'.
        --output: Name of the output file, defaults to 'output.txt'.
    Returns:
        The parser with all the arguments.
    """

    parser = argparse.ArgumentParser(description='Collect and convert JSON data to CSV file.')
    parser.add_argument('-i', '--input_data_folder', default='data', help='Name of the input data folder.')
    parser.add_argument('-o', '--output', default='output.csv', help='Name of the output file.')
    return parser


def main():
    """ Reads JSON files from input data folder and saves as CSV with labeled sentiments.
    Labels are 1 for positive, 0 for negative.
    """

    POSITIVE = 1
    NEGATIVE = 0

    parser = prepare_parser()
    args = parser.parse_args()

    csv_file = csv.writer(open(args.output, "w"))
    csv_file.writerow(["review", "sentiment"])
    for filename in os.listdir(args.input_data_folder):
        data = json.load(open(args.input_data_folder + '/' + filename))
        for entry in data:
            if entry['positive']:
                csv_file.writerow([entry['positive'].encode('utf8'), POSITIVE])
            if entry['negative']:
                csv_file.writerow([entry['negative'].encode('utf8'), NEGATIVE])


if __name__ == '__main__':
    main()
