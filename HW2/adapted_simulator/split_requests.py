
import argparse

from hw2_utils import TraceEntry

# Example for getting command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("input", type=str, help="path to input file")
parser.add_argument("output", type=str, help="path to output file.")

args = parser.parse_args()

with open(args.input) as in_fd, open(args.output, 'w') as out_fd:
    for line in in_fd:
        for entry in TraceEntry(line).split_blocks():
            out_fd.write("{}\n".format(str(entry)))