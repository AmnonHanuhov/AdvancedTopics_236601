from copy import deepcopy
import argparse

class TraceEntry():
    def __init__(self, line):
        time, disk, block, size, self.op, delta = line.split()
        self.time, self.delta = float(time), float(delta)
        self.disk, self.block, self.size = int(disk), int(block), int(size)
        self.hit = None

    # Returns a default string representation for the entry
    # including additional field for H/M reult
    def __str__(self):
        return "{} {} {} {} {} {} {}".format(
            "%.6f"%self.time,
            self.disk,
            self.block,
            self.size,
            self.op,
            "%.6f"%self.delta,
            {None:"", False:"M", True:"H"}[self.hit]
        )

    # Splits a multi-block request to a list of single-block ones
    def split_blocks(self):
        blocks = [deepcopy(self) for i in range(self.size)]
        for i in range(len(blocks)):
            blocks[i].block = self.block + i
            blocks[i].size = 1
        return blocks


# Example for getting command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("input", type=str, help="path to input file")
parser.add_argument("output", type=str, help="path to output file.")

args = parser.parse_args()

with open(args.input) as in_fd, open(args.output, 'w') as out_fd:
    for line in in_fd:
        for entry in TraceEntry(line).split_blocks():
            out_fd.write("{}\n".format(str(entry)))
