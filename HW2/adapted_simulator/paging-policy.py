#! /usr/bin/env python

from optparse import OptionParser import random

from hw2_utils import TraceEntry, CacheEntry
from dlist import DList, Node

MEM_LISTS = 6
NOT_FOUND = (-1, -1)

FIFO_L = 0
LRU_L = 1
FIFO_GHOST_L = 2
LRU_GHOST_L = 3


# Looks for a (non-ghost) entry in the memory.
# Returns (list_num, index):
#   list_num: which list in memory contains entry
#   index: index of entry in said memory list
# (if not found, returns -1 for both)
def find_entry(memory, mem_dict, LBA):
    ce = CacheEntry(LBA, False)
    if policy == 'HW2':
        for li in range(0, 2):
            if ce in memory[li]:
                return (li, 0)
        return NOT_FOUND

    if policy != 'RAND':
        if ce not in memory[0]:
            return NOT_FOUND
        return (0, 0)

    if (LBA, False) not in mem_dict:
        return NOT_FOUND
    return mem_dict[(LBA, False)]

# Looks for a ghost entry in the memory
# format same as find_entry
def find_ghost(memory, mem_dict, LBA):
    ce = CacheEntry(LBA, True)
    if policy == 'HW2':
        for li in range(2, 4):
            if ce in memory[li]:
                return (li, 0)
        return NOT_FOUND

    if policy != 'RAND':
        if ce not in memory[0]:
            return NOT_FOUND
        return (0, 0)

    if (LBA, True) not in mem_dict:
        return NOT_FOUND
    return mem_dict[(LBA, True)]

# Asserts that the limit on cache capacity is not broken
def check_mem_limit(memory, limit):
    return sum(map(lambda m: len(m), memory)) <= limit

#
# main program
#
parser = OptionParser()
parser.add_option('-f', '--addressfile', default='',   help='a file with a bunch of addresses in it',                                action='store', type='string', dest='addressfile')
parser.add_option('-p', '--policy', default='FIFO',    help='replacement policy: FIFO, LRU, RAND',                                   action='store', type='string', dest='policy')
parser.add_option('-C', '--cachesize', default='3',    help='size of the page cache, in pages',                                      action='store', type='string', dest='cachesize')
parser.add_option('-s', '--seed', default='0',         help='random number seed',                                                    action='store', type='string', dest='seed')
parser.add_option('-N', '--notrace', default=False,    help='do not print out a detailed trace',                                     action='store_true', dest='notrace')
parser.add_option('-S', '--split', default=False,    help='split every multi-block request into many single-block ones',             action='store_true', dest='split')

(options, args) = parser.parse_args()

if options.addressfile == '':
    parser.error('Address file not given')

print('ARG addressfile', options.addressfile)
print('ARG policy', options.policy)
print('ARG cachesize', options.cachesize)
print('ARG seed', options.seed)
print('ARG notrace', options.notrace)
print('ARG split', options.split)
print('')

addressFile = str(options.addressfile)
cachesize   = int(options.cachesize)
seed        = int(options.seed)
policy      = str(options.policy)
notrace     = options.notrace
split       = options.split

random.seed(seed)

# init memory structure
count = 0
# p = int(cachesize / 2)
p = 0

if policy == 'RAND':
    # memory is an array of 6 lists
    # regular pre-defined algorithms use only memory[0] (the first list),
    # you may use up to all 6 to implement any logic of your choice
    memory = []
    [memory.append([]) for i in range(0, MEM_LISTS)]
else: # in our policy we use a different data structure
    memory = [DList() for i in range(0, MEM_LISTS)]

# mem_dict is a simple hash-table that MUST reflect the memory state.
# maps pairs of (LBA, ghost_bool) to (list_num, idx) indices that point
# the entry location inside memory (detailed explanation in README)
mem_dict = {}

hits = 0
miss = 0

if policy not in ["FIFO", "LRU", "MRU", "RAND", "HW2"]:
    print('Policy %s is not yet implemented' % policy)
    exit(1)

def replace(gce):
    global miss, hits, count, p, mem_dict, memory, addrList
    if (len(memory[FIFO_L]) > 0) and ((len(memory[FIFO_L]) > p) or (gce in memory[LRU_GHOST_L] and len(memory[FIFO_L]) == p)):
        victim = memory[FIFO_L].pop_front()
        gce = CacheEntry(victim.LBA, True)
        memory[FIFO_GHOST_L].append(gce)
    else:
        victim = memory[LRU_L].pop_front()
        gce = CacheEntry(victim.LBA, True)
        memory[LRU_GHOST_L].append(gce)
    return victim


def ARC(te):
    global miss, hits, count, p, mem_dict, memory, addrList
    if len(memory[LRU_L]) == 0:
        ratio = 1.0
    else:
        ratio = len(memory[FIFO_L])/len(memory[LRU_L])

    # first, lookup
    addr = te.block
    list_num, idx = find_entry(memory, mem_dict, addr)

    if ((list_num, idx) != NOT_FOUND):
        hits = hits + 1
        te.hit = True
        ce = CacheEntry(addr)
        # either move the block from FIFO to LRU or promote the block inside LRU to be the head
        memory[list_num].pop(ce)
        memory[LRU_L].append(ce)
    else:
        ce = CacheEntry(addr) # create a new non-ghost entry for the new address
        miss = miss + 1
        te.hit = False
        gce = CacheEntry(addr, True)
        ghost_list_num, ghost_idx = find_ghost(memory, mem_dict, addr)
        if ghost_list_num == FIFO_GHOST_L:
            if len(memory[FIFO_L]) != 0:
                p = min(cachesize, p + max(1, int(len(memory[LRU_L]) / len(memory[FIFO_L]))))
            else:
                p = cachesize
            replace(gce)
            memory[FIFO_GHOST_L].pop(gce)
            memory[LRU_L].append(ce)
        elif ghost_list_num == LRU_GHOST_L:
            if len(memory[LRU_L]) != 0:
                p = max(0, p - max(1, int(len(memory[FIFO_L]) / len(memory[LRU_L]))))
            else:
                p = 0
            replace(gce)
            memory[LRU_GHOST_L].pop(gce)
            memory[LRU_L].append(ce)
        else: # not in cache and ghost-cache
            if len(memory[FIFO_L]) + len(memory[FIFO_GHOST_L]) == cachesize:
                if len(memory[FIFO_L]) < cachesize:
                    memory[FIFO_GHOST_L].pop_front()
                    victim = replace(gce)
                else:
                    victim = memory[FIFO_L].pop_front()
            elif len(memory[FIFO_L]) + len(memory[FIFO_GHOST_L]) < cachesize:
                if sum(map(lambda m: len(m), memory)) >= cachesize:
                    if sum(map(lambda m: len(m), memory)) == 2*cachesize:
                        memory[LRU_GHOST_L].pop_front()
                    replace(gce)
            memory[FIFO_L].append(ce)

    assert(check_mem_limit(memory, 2*cachesize))
    if notrace == False:
        print(te)

addrList = []
fd = open(addressFile)
for line in fd:
    if (split):
        # split multi-block requests into single-block requests
        addrList = TraceEntry(line).split_blocks()
    else:
        addrList = [TraceEntry(line), ]

    for te in addrList:
        if policy == 'HW2':
            ARC(te)
            continue

        # first, lookup
        addr = te.block
        list_num, idx = find_entry(memory, mem_dict, addr)

        ce = CacheEntry(addr) # create a new non-ghost entry for the new address
        if ((list_num, idx) == NOT_FOUND):
            idx = -1
            miss = miss + 1
            te.hit = False
        else: # found in cache
            hits = hits + 1
            te.hit = True
            if policy == 'LRU' or policy == 'MRU':
                memory[0].pop(ce)
                memory[0].append(ce) # puts it on MRU side

        victim = -1
        if idx == -1:
            # miss, replace?
            if count == cachesize:
                # must replace
                if policy == 'FIFO' or policy == 'LRU':
                    victim = memory[0].pop_front()
                elif policy == 'MRU':
                    victim = memory[0].pop_back()
                elif policy == 'RAND':
                    victim = memory[0].pop(int(random.random() * count))
                    del mem_dict[(victim.LBA, victim.ghost)]

            else:
                # miss, but no replacement needed (cache not full)
                victim = -1
                count = count + 1

            memory[0].append(ce)
            if policy == 'RAND':
                # when CaceEntry enters memory, it's key must be added to hash
                mem_dict[(ce.LBA, ce.ghost)] = (0, len(memory[0])-1)

            
            if victim != -1:
                assert(find_entry(memory, mem_dict, victim) == NOT_FOUND)

        # if you fail this assertion, you have exceeded your cache space capacity.
        assert(check_mem_limit(memory, 2*cachesize))

        if notrace == False:
            print(te)

fd.close()
print('')
print('FINALSTATS hits %d   misses %d   hitrate %.5f' % (hits, miss, (100.0*float(hits))/(float(hits)+float(miss))))
print('')













