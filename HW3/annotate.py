#! /usr/bin/env python

from time import localtime
import argparse
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
parser = argparse.ArgumentParser()
parser.add_argument('input', type=str)
parser.add_argument('annotation', type=str)
parser.add_argument('stat', type=str)
args = parser.parse_args()

input = str(args.input)
annotation   = str(args.annotation)
stat = str(args.stat)
print(input, annotation, stat)

split       = True
memory = [DList() for i in range(0, MEM_LISTS)]
tempreture_stat = [0 for i in range(0, MEM_LISTS)]
average_counter = 0

with open(input) as in_fd, open(annotation, 'w') as annotation_fd, open(stat, 'w') as stat_fd:
    for line in in_fd:
        if (split):
            block_list = TraceEntry(line).split_blocks()
        else:
            block_list = [TraceEntry(line)]

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
                while counter > (2 ** tempreture_i) * average_counter and tempreture_i < MEM_LISTS - 1:
                    tempreture_i = tempreture_i + 1
                memory[tempreture_i].append(CacheEntry(addr), counter)


            tempreture_num = find_entry(memory, addr)
            te.set_tempreture(10-tempreture_num)
            tempreture_stat[tempreture_num] = tempreture_stat[tempreture_num] + 1
            print(te, file=annotation_fd)

        average_counter = average_counter + len(block_list) / sum(map(lambda m: len(m), memory))

    # print(tempreture_stat, file=stat_fd)
    print(tempreture_stat)
    
