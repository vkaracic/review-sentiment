import argparse
import csv
import os

import json


def prepare_parser():
    """ Parse the command line arguments.

    Arguments:
        --input: Name of the input file, defaults to 'input.txt'.
        --output: Name of the output file, defaults to 'output.txt'.
    Returns:
        The parser with all the arguments.
    """

    parser = argparse.ArgumentParser(description='Collect and convert JSON data to CSV file.')
    parser.add_argument('-i', '--input_data_folder', default='data', help='Name of the input data folder.')
    parser.add_argument('-o', '--output', default='output.csv', help='Name of the output file.')
    return parser


def main():
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
