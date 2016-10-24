"""
Script for running SyntaxNet parser on a file with reviews and output the
parsed tree to an output file. Because there isn't a way of calling the
parser in the usual Python way, this script runs the parser with a shell command
as a subprocess and therefor heavily relies on proper directory paths.

The 'models' directory where SytnaxNet is contained should be in the same
directory level as the directory where this script is contained, otherwise
the SCRIPT_ROOT and ROOT_DIR contants need to adjusted accordingly.

Adjust your 'syntaxnet/demo.sh' file for a different output.
"""
import argparse
import os
import subprocess

# Path to the root directory of this script.
SCRIPT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Path to the directory where SyntaxNet is installed.
ROOT_DIR = '{}/models/syntaxnet'.format(
    os.path.dirname(SCRIPT_ROOT)
)


def prepare_parser():
    """ Parse the command line arguments.

    Arguments:
        --input: Name of the input file, defaults to 'input.txt'.
        --output: Name of the output file, defaults to 'output.txt'.
    Returns:
        The parser with all the arguments.
    """

    parser = argparse.ArgumentParser(description='Parse a file with SyntaxNet.')
    parser.add_argument('-i', '--input', default='input.txt', help='Name of the input file.')
    parser.add_argument('-o', '--output', default='output.txt', help='Name of the output file.')
    return parser


def run_syntaxnet(text):
    """ Run the SyntaxNet parser as a subprocess since there
    is no other way to run it at this time.

    Arguments:
        text (str): The text that is parsed.

    Returns:
        Output of the shell command.
    """
    process = subprocess.Popen([
        "echo '{}' | syntaxnet/demo.sh".format(text)
    ], stdout=subprocess.PIPE, shell=True)
    return process.communicate()[0]


def main():
    """ Parse all the lines in the input file and save the outputs to the output file. """
    parser = prepare_parser()
    args = parser.parse_args()
    input_path = '{}/{}'.format(SCRIPT_ROOT, args.input)
    output_path = '{}/{}'.format(SCRIPT_ROOT, args.output)

    # The working directory needs to be the SyntaxNet root directory
    # because the parser won't work otherwise.
    os.chdir(ROOT_DIR)

    parsed_text = []
    with open(input_path, 'r') as input_file:
        data = input_file.read().splitlines()
        for text in data:
            output = run_syntaxnet(text)
            parsed_text.append(output)

    with open(output_path, 'w') as output_file:
        for text in parsed_text:
            output_file.write(str(text))


if __name__ == '__main__':
    main()
