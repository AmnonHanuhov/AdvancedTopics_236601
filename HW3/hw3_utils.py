from copy import deepcopy

class TraceEntry():
    def __init__(self, line):
        time, disk, block, size, self.op, delta = line.split()
        self.time, self.delta = float(time), float(delta)
        self.disk, self.block, self.size = int(disk), int(block), int(size)
        self.hit = None

        # temperature defaults at 10 - you should change it from outside
        self.temperature = 10

    def set_tempreture(self, tempreture):
        self.temperature = tempreture
        
    # Returns a default string representation for the entry
    def __str__(self):
        return "{} {} {} {} {} {}".format(
            "%.6f"%self.time,
            self.disk,
            self.block,
            self.size,
            self.op,
            self.temperature
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
