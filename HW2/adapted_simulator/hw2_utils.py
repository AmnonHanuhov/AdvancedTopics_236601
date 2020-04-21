from copy import deepcopy

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

# A wrapper class to represent an entry.
class CacheEntry():
    def __init__(self, LBA, ghost=False, metadata=None):
        self.LBA, self.ghost, self.metadata = LBA, ghost, metadata

    def __eq__(self, other):
        if isinstance(other, CacheEntry):
            return (self.LBA, self.ghost) == (other.LBA, other.ghost)
        return NotImplemented

    def __hash__(self):
        return hash((self.LBA, self.ghost))