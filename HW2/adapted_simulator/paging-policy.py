#! /usr/bin/env python

from optparse import OptionParser
import random

from hw2_utils import TraceEntry, CacheEntry

MEM_LISTS = 6
NOT_FOUND = (-1, -1)

# Looks for a (non-ghost) entry in the memory.
# Returns (list_num, index):
#   list_num: which list in memory contains entry
#   index: index of entry in said memory list
# (if not found, returns -1 for both)
def find_entry(memory, mem_dict, LBA):
    if (LBA, False) not in mem_dict:
        return NOT_FOUND
    return mem_dict[(LBA, False)]

# Looks for a ghost entry in the memory
# format same as find_entry
def find_ghost(memory, mem_dict, LBA):
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
# memory is an array of 6 lists
# regular pre-defined algorithms use only memory[0] (the first list),
# you may use up to all 6 to implement any logic of your choice
memory = []
[memory.append([]) for i in range(MEM_LISTS)]

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
        ce = memory[list_num][idx] # get the existing non-ghost entry from cache
        hits = hits + 1
        te.hit = True
        if policy == 'LRU' or policy == 'MRU':
            del memory[0][idx]
            memory[0].append(ce) # puts it on MRU side
            mem_dict[ce] = (0, 0) # MUST update value in the hash table

    victim = -1      
    if idx == -1:
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
                pass
                # # # # #
                # TODO: Your eviction policy code goes here
                # # # # #

            # when CacheEntry leaves memory, it's key must be removed from the hash table
            del mem_dict[(victim.LBA, victim.ghost)]
        else:
            # miss, but no replacement needed (cache not full)
            victim = -1
            count = count + 1

        # now add to memory
        if policy != 'HW2':
            memory[0].append(ce)
            # when CaceEntry enters memory, it's key must be added to hash
            mem_dict[(ce.LBA, ce.ghost)] = (0, len(memory[0])-1)
        if policy == 'HW2':
            pass
            # # # # #
            # TODO: Insert the new entry into the one of the memory lists according to your policy
            # # # # #

        if victim != -1:
            assert(find_entry(memory, mem_dict, victim) == NOT_FOUND)

    # if you fail this assertion, you have exceeded your cache space capacity.
    assert(check_mem_limit(memory, 2*cachesize))

    if notrace == False:
        print(te)
    
print('')
print('FINALSTATS hits %d   misses %d   hitrate %.5f' % (hits, miss, (100.0*float(hits))/(float(hits)+float(miss))))
print('')













