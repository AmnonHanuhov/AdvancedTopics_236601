#! /usr/bin/env python

from optparse import OptionParser
import random

from hw2_utils import TraceEntry, CacheEntry
from dlist import DList, Node

MEM_LISTS = 6
NOT_FOUND = (-1, -1)
HW2_NOT_FOUND = (-1, -1, -1)

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
    if policy == 'HW2':
        ce = CacheEntry(LBA, False)
        for li in range(0, 2):
            if ce in memory[li]:
                return (li, 0)
        return NOT_FOUND

    if (LBA, False) not in mem_dict:
        return NOT_FOUND
    return mem_dict[(LBA, False)]

# Looks for a ghost entry in the memory
# format same as find_entry
def find_ghost(memory, mem_dict, LBA):
    if policy == 'HW2':
        ce = CacheEntry(LBA, True)
        for li in range(2, 4):
            if ce in memory[li]:
                return (li, 0)
        return NOT_FOUND

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

addrList = []
fd = open(addressFile)
for line in fd:
    if (split):
        # split multi-block requests into single-block requests
        addrList += TraceEntry(line).split_blocks()
    else:
        addrList.append(TraceEntry(line))
fd.close()

# init memory structure
count = 0
p = int(cachesize / 2)

# memory is an array of 6 lists
# regular pre-defined algorithms use only memory[0] (the first list),
# you may use up to all 6 to implement any logic of your choice
memory = []
[memory.append([]) for i in range(MEM_LISTS)]
if policy == 'HW2':
    memory = [DList() for i in range(0, MEM_LISTS)]

# mem_dict is a simple hash-table that MUST reflect the memory state.
# maps pairs of (LBA, ghost_bool) to (list_num, idx) indices that point
#   the entry location inside memory (detailed explanation in README)
mem_dict = {}

hits = 0
miss = 0

if policy not in ["FIFO", "LRU", "MRU", "RAND", "HW2"]:
    print('Policy %s is not yet implemented' % policy)
    exit(1)

for te in addrList:
    # first, lookup
    addr = te.block
    list_num, idx = find_entry(memory, mem_dict, addr)

    if ((list_num, idx) == NOT_FOUND):
        ce = CacheEntry(addr) # create a new non-ghost entry for the new address
        idx = -1
        miss = miss + 1
        te.hit = False
    else: # found in cache
        if policy != 'HW2':
            ce = memory[list_num][idx] # get the existing non-ghost entry from cache
        hits = hits + 1
        te.hit = True
        if policy == 'LRU' or policy == 'MRU':
            del memory[0][idx]
            memory[0].append(ce) # puts it on MRU side
            mem_dict[ce] = (0, 0) # MUST update value in the hash table
        if policy == 'HW2':
            # memory[list_num].remove(ce)
            # memory[LRU_L].append(ce) # puts it on MRU side
            # mem_dict[(ce.LBA, ce.ghost)] = (LRU_L,  0, memory[LRU_L][-1])
            ce = CacheEntry(addr)
            if ce in memory[LRU_L]:
                memory[LRU_L].pop(ce)
            else:
                memory[FIFO_L].pop(ce)
            memory[LRU_L].append(ce)

    victim = -1      
    if idx == -1:
        # miss, search in ghost cache,
        if policy == 'HW2':
            next_list = FIFO_L
            ghost_list_num, ghost_idx = find_ghost(memory, mem_dict, addr)
            if (ghost_list_num, ghost_idx) != NOT_FOUND: # ghost cache hit, change p
                next_list = LRU_L
                memory[ghost_list_num].pop(CacheEntry(addr, True))
                if ghost_list_num == FIFO_GHOST_L:
                    if len(memory[FIFO_L]) != 0:
                        p = p + max(1, int(len(memory[LRU_L]) / len(memory[FIFO_L])))
                    else:
                        p = cachesize
                else:
                    if len(memory[LRU_L]) != 0:
                        p = max(0, p - max(1, int(len(memory[FIFO_L]) / len(memory[LRU_L]))))
                    else:
                        p = 0

        # miss, replace?
        if count == cachesize:
            # must replace
            if policy == 'FIFO' or policy == 'LRU':
                victim = memory[0].pop(0)
            elif policy == 'MRU':
                victim = memory[0].pop(count-1)
            elif policy == 'RAND':
                victim = memory[0].pop(int(random.random() * count))
            elif policy == "HW2":
                if len(memory[FIFO_L]) <= p or len(memory[FIFO_L]) == 0:
                    victim = memory[LRU_L].pop_front()
                    # if len(memory[LRU_GHOST_L]) == len(memory[FIFO_L]):
                    gce = CacheEntry(victim.LBA, True)
                    memory[LRU_GHOST_L].append(gce)
                    # mem_dict[(victim.LBA, True)] = (LRU_GHOST_L, 0, memory[LRU_GHOST_L][-1])
                else:
                    victim = memory[FIFO_L].pop_front()
                    # if len(memory[FIFO_GHOST_L]) == len(memory[LRU_L]):
                    gce = CacheEntry(victim.LBA, True)
                    memory[FIFO_GHOST_L].append(gce)
                    # mem_dict[(victim.LBA, True)] = (FIFO_GHOST_L, 0, memory[FIFO_GHOST_L][-1])
                                
            if policy != 'HW2':
                # when CacheEntry leaves memory, it's key must be removed from the hash table
                del mem_dict[(victim.LBA, victim.ghost)]
        else:
            # miss, but no replacement needed (cache not full)
            victim = -1
            count = count + 1

        # now add to memory
        if policy == 'HW2':
            if sum(map(lambda m: len(m), memory)) == 2*cachesize:
                if memory[next_list+2].size != 0:
                    memory[next_list+2].pop_front()
                else:
                    memory[((next_list+1)%2)+2].pop_front()
            memory[next_list].append(ce)
            # mem_dict[(ce.LBA, ce.ghost)] = (next_list,  0, memory[next_list][-1])
        else:
            memory[0].append(ce) # insert on MRU side
            # when CaceEntry enters memory, it's key must be added to hash
            mem_dict[(ce.LBA, ce.ghost)] = (0, len(memory[0])-1)
        
        if victim != -1:
            assert(find_entry(memory, mem_dict, victim.LBA) == NOT_FOUND)

    # if you fail this assertion, you have exceeded your cache space capacity.
    assert(check_mem_limit(memory, 2*cachesize))

    if notrace == False:
        print(te)
    
print('')
print('FINALSTATS hits %d   misses %d   hitrate %.5f' % (hits, miss, (100.0*float(hits))/(float(hits)+float(miss))))
print('')













