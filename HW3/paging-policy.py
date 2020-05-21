#! /usr/bin/env python

from time import localtime
from optparse import OptionParser
import random
from hw3_utils import TraceEntry, CacheEntry
from dlist import DList

MEM_LISTS = 8
NOT_FOUND = -1

FIFO_L = 0
LRU_L = 1
FIFO_GHOST_L = 2
LRU_GHOST_L = 3


# Looks for a (non-ghost) entry in the memory.
# Returns (list_num, index):
#   list_num: which list in memory contains entry
#   index: index of entry in said memory list
# (if not found, returns -1 for both)
def find_entry(memory, LBA):
    ce = CacheEntry(LBA, False)
    for li in range(0, 8):
        if ce in memory[li]:
            return li
    return NOT_FOUND

# Asserts that the limit on cache capacity is not broken
def check_mem_limit(memory, limit):
    return sum(map(lambda m: len(m), memory)) <= limit

#
# main program
#
parser = OptionParser()
parser.add_option('-f', '--addressfile', default='',   help='a file with a bunch of addresses in it',                                action='store', type='string', dest='addressfile')
parser.add_option('-p', '--policy', default='FIFO',    help='replacement policy: FIFO, LRU, RAND',                                   action='store', type='string', dest='policy')
parser.add_option('-C', '--cachesize', default='4096',    help='size of the page cache, in pages',                                      action='store', type='string', dest='cachesize')
parser.add_option('-s', '--seed', default='0',         help='random number seed',                                                    action='store', type='string', dest='seed')
parser.add_option('-S', '--split', default=True,    help='split every multi-block request into many single-block ones',             action='store_true', dest='split')

(options, args) = parser.parse_args()

if options.addressfile == '':
    parser.error('Address file not given')

addressFile = str(options.addressfile)
cachesize   = int(options.cachesize)
seed        = int(options.seed)
policy      = str(options.policy)
split       = options.split

random.seed(seed)

memory = [DList() for i in range(0, MEM_LISTS)]
tempreture_stat = [0 for i in range(0, MEM_LISTS)]
average_counter = 0

with open(addressFile) as fd:
    for fd_line in fd:
        if (split):
            block_list = TraceEntry(fd_line).split_blocks()
        else:
            block_list = [TraceEntry(fd_line)]

        for te in block_list:
            # first, lookup
            addr = te.block
            tempreture_num = find_entry(memory, addr)

            if (tempreture_num == NOT_FOUND):
                te.hit = False
                memory[0].append(CacheEntry(addr))
            else:
                te.hit = True
                counter = memory[tempreture_num].pop(CacheEntry(addr)) # returns prev counter of CacheEntry
                counter = counter + 1

                tempreture_i = 0
                while counter > (3 ** tempreture_i) * average_counter and tempreture_i < MEM_LISTS - 1:
                    tempreture_i = tempreture_i + 1
                memory[tempreture_i].append(CacheEntry(addr), counter)

            assert(check_mem_limit(memory, 2*cachesize))


            tempreture_num = find_entry(memory, addr)
            te.set_tempreture(10-tempreture_num)
            tempreture_stat[tempreture_num] = tempreture_stat[tempreture_num] + 1
            print(te)

        average_counter = average_counter + len(block_list) / sum(map(lambda m: len(m), memory))

print(tempreture_stat)
    
