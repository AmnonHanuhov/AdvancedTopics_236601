#! /usr/bin/env python

from time import localtime
import argparse
import math
import random
from hw3_utils import TraceEntry, CacheEntry
from dlist import DList

MEM_LISTS = 6
NOT_FOUND = -1

FIFO_L = 0
LRU_L = 1
FIFO_GHOST_L = 2
LRU_GHOST_L = 3


# Looks for a entry in the memory.
# Returns list_num:
#   list_num: which list in memory contains entry
# if not found, returns -1
def find_entry(memory, LBA):
    for li in range(0, MEM_LISTS):
        if CacheEntry(LBA, False) in memory[li]:
            return li
    return NOT_FOUND

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

# initialization of the annotator's global variables
memory          = [DList() for i in range(0, MEM_LISTS)]
tempreture_stat = [0 for i in range(0, MEM_LISTS)]

high_page_count = 1                     # number of valid pages with high IRG
low_page_count = 1                      # number of valid pages with low IRG
high_average_counter = 0                # approximated average access count for pages with high IRG
low_average_counter = 0                 # approximated average access count for pages with low IRG
average_irg = 0                         # moving average IRG of all accesses

with open(input) as in_fd, open(annotation, 'w') as annotation_fd, open(stat, 'w') as stat_fd:
    for time, line in enumerate(in_fd):
        block_list = TraceEntry(line).split_blocks()

        for te in block_list:
            # first, lookup
            addr = te.block
            tempreture_num = find_entry(memory, addr)
            irg = 0

            if (tempreture_num == NOT_FOUND):
                te.hit = False
                memory[0].append(CacheEntry(addr))    # new pages are added to the coldest list of with high IRG
                high_page_count = high_page_count + 1 # thus increment the total high pages count
            else:
                te.hit = True
                # pop current accessed page from memory and update its counter
                counter, last_update_time = memory[tempreture_num].pop(CacheEntry(addr)) 
                counter = counter + 1

                # update valid pages in the partition
                if tempreture_num < MEM_LISTS/2:
                    high_page_count = high_page_count - 1
                else:
                    low_page_count = low_page_count - 1

                # calculate irg and handle both partitions
                irg = time - last_update_time
                high_irg = irg > average_irg
                if high_irg:
                    tempreture_i = 0
                    while counter > (1.5 ** tempreture_i) * high_average_counter and tempreture_i < int((MEM_LISTS - 1)/2):
                        tempreture_i = tempreture_i + 1

                    # found new tempreture, append with updated metadata and system counters
                    memory[tempreture_i].append(CacheEntry(addr), counter, time)
                    high_average_counter = high_average_counter + 1 / high_page_count
                    high_page_count = high_page_count + 1
                else:
                    tempreture_i = 0
                    while counter > (1.5 ** tempreture_i) * low_average_counter and tempreture_i < int((MEM_LISTS - 1)/2):
                        tempreture_i = tempreture_i + 1
                        
                    # found new tempreture, append with updated metadata and system counters
                    memory[tempreture_i + int(MEM_LISTS/2)].append(CacheEntry(addr), counter, time)
                    low_average_counter = low_average_counter + 1 / low_page_count
                    low_page_count = low_page_count + 1
                    
            average_irg = (irg + time * average_irg) / (time + 1)  # update the moving average irg of all accesses

            # find page's current tempreture(as defined in class) and update te's new tempreture for it
            tempreture_num = find_entry(memory, addr) 
            te.set_tempreture(MEM_LISTS-tempreture_num)
            print(te, file=annotation_fd)
            # update trace statistics
            tempreture_stat[MEM_LISTS-tempreture_num-1] = tempreture_stat[MEM_LISTS-tempreture_num-1] + 1

    print(tempreture_stat, file=stat_fd)
