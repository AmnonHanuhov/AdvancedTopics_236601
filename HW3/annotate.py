#! /usr/bin/env python

from time import localtime
import argparse
import random
from hw3_utils import TraceEntry, CacheEntry
from dlist import DList

MEM_LISTS = 10
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
    for li in range(0, MEM_LISTS):
        if CacheEntry(LBA, False) in memory[li]:
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

split           = True
memory          = [DList() for i in range(0, MEM_LISTS)]
tempreture_stat = [0 for i in range(0, MEM_LISTS)]

high_page_count = 1
low_page_count = 1
high_average_counter = 0
low_average_counter = 0
average_irg     = 0

with open(input) as in_fd, open(annotation, 'w') as annotation_fd, open(stat, 'w') as stat_fd:
    for time, line in enumerate(in_fd):
        if (split):
            block_list = TraceEntry(line).split_blocks()
        else:
            block_list = [TraceEntry(line)]

        for te in block_list:
            # first, lookup
            addr = te.block
            tempreture_num = find_entry(memory, addr)
            irg = 0

            if (tempreture_num == NOT_FOUND):
                te.hit = False
                memory[0].append(CacheEntry(addr))
                high_page_count = high_page_count + 1
            elif True:
                te.hit = True
                counter, last_update_time = memory[tempreture_num].pop(CacheEntry(addr)) # returns prev counter of CacheEntry
                counter = counter + 1
                irg = time - last_update_time

                tempreture_i = 0
                while counter > (1.5 ** tempreture_i) * high_average_counter and tempreture_i < MEM_LISTS-1:
                    tempreture_i = tempreture_i + 1
                memory[tempreture_i].append(CacheEntry(addr), counter, time)
                high_average_counter = high_average_counter + 1 / sum(map(lambda m: len(m), memory))
            else:
                te.hit = True
                counter, last_update_time = memory[tempreture_num].pop(CacheEntry(addr)) # returns prev counter of CacheEntry
                counter = counter + 1
                irg = time - last_update_time
                if tempreture_num < MEM_LISTS/2:
                    high_page_count = high_page_count - 1
                else:
                    low_page_count = low_page_count - 1

                high_irg = irg > average_irg
                if high_irg:
                    tempreture_i = 0
                    while counter > (1.5 ** tempreture_i) * high_average_counter and tempreture_i < int((MEM_LISTS - 1)/2):
                        tempreture_i = tempreture_i + 1
                    memory[tempreture_i].append(CacheEntry(addr), counter, time)
                    high_average_counter = high_average_counter + 1 / high_page_count
                    high_page_count = high_page_count + 1
                else:
                    tempreture_i = 0
                    while counter > (1.5 ** tempreture_i) * low_average_counter and tempreture_i < int((MEM_LISTS - 1)/2):
                        tempreture_i = tempreture_i + 1
                    memory[tempreture_i + int(MEM_LISTS/2)].append(CacheEntry(addr), counter, time)
                    low_average_counter = low_average_counter + 1 / low_page_count
                    low_page_count = low_page_count + 1

            average_irg = (irg + time * average_irg) / (time + 1)

            # find page's current tempreture and update te's new tempreture for it
            tempreture_num = find_entry(memory, addr) 
            te.set_tempreture(MEM_LISTS-tempreture_num)
            print(te, file=annotation_fd)
            # update tempreture statistics
            tempreture_stat[MEM_LISTS-tempreture_num-1] = tempreture_stat[MEM_LISTS-tempreture_num-1] + 1

        # average_counter = average_counter + len(block_list) / sum(map(lambda m: len(m), memory))

    # print(tempreture_stat, file=stat_fd)
    print(tempreture_stat, '\nlow avg counter: ', low_average_counter, 'high avg counter: ',high_average_counter)
