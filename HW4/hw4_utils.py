class TraceEntry():
    def __init__(self, line):
        time, disk, block, size, self.op, delta, FP = line.split()
        self.time, self.delta = float(time), float(delta)
        self.disk, self.block, self.size = int(disk), int(block), int(size)
        self.hit = None
        self.FP = int(FP, 16)

    # Returns a default string representation for the entry
    def __str__(self):
        return "{} {} {} {} {} {} {}".format(
            "%.6f" % self.time,
            self.disk,
            self.block,
            self.size,
            self.op,
            "%.6f" % self.delta,
            {None: "", False: "M", True: "H"}[self.hit],
        )


"""
A wrapper class for a cached LBA representation.
Contains:
    The LBA itself (an integer block number).
    An integer fingerprint (FP) that represents the data stored in the matching LBA
"""
class LBAItem():
    def __init__(self, LBA, FP, metadata=None):
        self.LBA, self.FP, self.metadata = LBA, FP, metadata

    def __eq__(self, other):
        if isinstance(other, LBAItem):
            return self.LBA == other.LBA
        return NotImplemented

    def __hash__(self):
        return hash(self.LBA)


"""
A wrapper class for a cached data block representation.
Contains:
    The fingerprint (FP) of the block (since we can't have actual data).
    in_cache: a boolean value denoting whether this block's data is currently cached.
"""
class FPItem():
    def __init__(self, FP, in_cache=False, metadata=None):
        self.FP, self.in_cache, self.metadata = FP, in_cache, metadata

    def __eq__(self, other):
        if isinstance(other, FPItem):
            return self.FP == other.FP
        return NotImplemented

    def __hash__(self):
        return hash(self.FP)
