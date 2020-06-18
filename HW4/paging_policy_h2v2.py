#! /usr/bin/env python

from optparse import OptionParser
import random
from hw4_utils import LBAItem, FPItem, TraceEntry
from dlist import DList, Node

MEM_LISTS = 8
ARC_LISTS = 4
NOT_FOUND = -1

FIFO_L = 0
LRU_L = 1
FIFO_GHOST_L = 2
LRU_GHOST_L = 3


# Asserts that the limit on cache capacity is not broken
def check_mem_limit(memory, cachesize):
    if policy == 'LRU':
        return sum(map(lambda m: len(m), memory)) <= 4 * cachesize  # 2 for LBA items and 2 for FP items
    if policy == 'HW4_LBA_ARC':
        return len(memory[1]) <= 2 * cachesize and sum(map(lambda m: len(m), memory[0])) <= 2 * cachesize
    if policy == 'HW4':
        return sum(map(lambda m: len(m), memory[0])) <= 2 * cachesize and sum(map(lambda m: len(m), memory[1])) <= 2 * cachesize


def replace(memory, p, item):
    if (len(memory[FIFO_L]) > 0) and ((len(memory[FIFO_L]) > p) or (item in memory[LRU_GHOST_L] and len(memory[FIFO_L]) == p)):
        victim = memory[FIFO_L].pop_front()
        if type(item) is FPItem:
            victim.in_cache = False
        memory[FIFO_GHOST_L].append(victim)
    else:
        victim = memory[LRU_L].pop_front()
        if type(item) is FPItem:
            victim.in_cache = False
        memory[LRU_GHOST_L].append(victim)
    return victim


def ARC(memory, p, count, item):
    if len(memory[LRU_L]) == 0:
        ratio = 1.0
    else:
        ratio = len(memory[FIFO_L])/len(memory[LRU_L])

    # FP_item = FPItem(F, in_cache=True)
    list_num = NOT_FOUND
    for i in range(0, 2):
        if item in memory[i]:
            list_num = i
            break;

    if (list_num != NOT_FOUND):
        te.hit = True
        # either move the block from FIFO to LRU or promote the block inside LRU to be the head
        item = memory[list_num].pop(item)
        memory[LRU_L].append(item)
    else:
        te.hit = False

        ghost_list_num = NOT_FOUND
        for i in range(2, 4):
            if item in memory[i]:
                ghost_list_num = i
                break;

        if ghost_list_num == FIFO_GHOST_L:
            if len(memory[FIFO_L]) != 0:
                p = min(cachesize, p + max(1, int(len(memory[LRU_L]) / len(memory[FIFO_L]))))
            else:
                p = 0.1 * cachesize
            replace(memory, p, item)
            item = memory[FIFO_GHOST_L].pop(item)
            if type(item) is FPItem:
                item.in_cache = True
            memory[LRU_L].append(item)
        elif ghost_list_num == LRU_GHOST_L:
            if len(memory[LRU_L]) != 0:
                p = max(0, p - max(1, int(len(memory[FIFO_L]) / len(memory[LRU_L]))))
            else:
                p = 0
            replace(memory, p, item)
            item = memory[LRU_GHOST_L].pop(item)
            if type(item) is FPItem:
                item.in_cache = True
            memory[LRU_L].append(item)
        else: # not in cache and ghost-cache
            if len(memory[FIFO_L]) + len(memory[FIFO_GHOST_L]) == cachesize:
                if len(memory[FIFO_L]) < cachesize:
                    memory[FIFO_GHOST_L].pop_front()
                    victim = replace(memory, p, item)
                else:
                    victim = memory[FIFO_L].pop_front()
                if type(item) is FPItem:
                    count -= 1
            elif len(memory[FIFO_L]) + len(memory[FIFO_GHOST_L]) < cachesize:
                if sum(map(lambda m: len(m), memory)) >= cachesize:
                    if sum(map(lambda m: len(m), memory)) == 2*cachesize:
                        memory[LRU_GHOST_L].pop_front()
                    replace(memory, p, item)
                    if type(item) is FPItem:
                        count -= 1
            memory[FIFO_L].append(item)
            if type(item) is FPItem:
                count += 1
            
    return item, p

#
# main program
#
parser = OptionParser()
parser.add_option('-f', '--addressfile', default='', help='path to the HW4 trace file', action='store', type='string', dest='addressfile')
parser.add_option('-p', '--policy', default='LRU', help='replacement policy: LRU/HW4', action='store', type='string', dest='policy')
parser.add_option('-C', '--cachesize', default='3', help='size of the page cache, in pages',  action='store', type='string', dest='cachesize')
parser.add_option('-N', '--notrace', default=False, help='do not print out a detailed trace', action='store_true', dest='notrace')

(options, args) = parser.parse_args()

if options.addressfile == '':
    parser.error('Address file not given')

addressFile = str(options.addressfile)
cachesize   = int(options.cachesize)
policy      = str(options.policy)
notrace     = options.notrace

# current cache capacity (FP items with in_cache=True)
count = 0

hits = 0
miss = 0

memory = []
if policy == 'LRU':
    # memory is an array of 6 lists
    # regular pre-defined algorithms use only memory[0] (the first list),
    # you may use up to all 6 to implement any logic of your choice
    [memory.append([]) for i in range(MEM_LISTS)]
if policy == 'HW4_LBA_ARC': # in our policy we use a different data structure
    memory.append([DList() for i in range(ARC_LISTS)])
    memory.append([])
if policy == 'HW4': 
    memory.append([DList() for i in range(ARC_LISTS)])
    memory.append([DList() for i in range(ARC_LISTS)])

class LBA_Dict(object):
    def __init__(self, memory):
        self.memory = memory

    def __contains__(self, L):
        item = LBAItem(L, 0)
        for l in self.memory:
            if item in l:
                return True
        return False

    def __getitem__(self, F):
        item = LBAItem(F, 0)
        for l in self.memory:
            if item in l:
                return l[item]

class FP_Dict(object):
    def __init__(self, memory):
        self.memory = memory

    def __contains__(self, F):
        FP_item = FPItem(F)
        for l in self.memory:
            if FP_item in l:
                return True
        return False

    def __getitem__(self, F):
        FP_item = FPItem(F)
        for l in self.memory:
            if FP_item in l:
                return l[FP_item]


# Each key (either integer LBA or integer FP) points to a matching LBAItem or FPItem in one of the memory lists.
# For convenience, the values are now references to the actual objects in the lists (not indices).
FP_dict  = {}
if policy == 'LRU':
    LBA_dict = {}
if policy == 'HW4_LBA_ARC':
    LBA_dict = LBA_Dict(memory[0])
if policy == 'HW4':
    LBA_dict = LBA_Dict(memory[0])
    FP_dict  = FP_Dict(memory[1])

LBA_p = 0
FP_p = 0

if policy not in ["LRU", "HW4", "HW4_LBA_ARC"]:
    print('Policy %s is not yet implemented' % policy)
    exit(1)


with open(addressFile) as fd:
    for fd_line in fd:
        te = TraceEntry(fd_line)
        L = te.block

        # First check if request hits or misses (result may vary according to request type, as stated in the pdf)
        # At the same time, determine the fingerprint (either look it up in the cache, or read it from the trace in case of a miss)
        if te.op == 'R': # Read path
            if (L in LBA_dict
                and LBA_dict[L].FP is not None 
                and LBA_dict[L].FP in FP_dict 
                and FP_dict[LBA_dict[L].FP].in_cache): # only if LBA exists and points at a fingerprint that is in cache

                F = LBA_dict[L].FP
                te.hit = True
                assert(F == te.FP) # if you fail here - there might be consistency problems in your cache (do not remove)
            else:
                F = te.FP # only allowed since we miss
                te.hit = False
        else: # Write path
            F = te.FP
            if F in FP_dict and FP_dict[F].in_cache:
                te.hit = True
            else:
                te.hit = False

        if (te.hit):
            hits += 1
        else:
            miss += 1

        # FIXME: when does an LBAItem.FP transfers to None? here and in the class presented algorithm

        # In this version, LRU uses memory[0] for LBA items and memory[1] for FP items
        if policy == "LRU":
            # Take care of replacing the fingerprint:
            if F in FP_dict:  # item exists in memory
                FP_item = FP_dict[F]
                memory[1].remove(FP_item)   # move the item to MRU end
                memory[1].append(FP_item)
                if not FP_item.in_cache:    # item should also be put in cache
                    FP_item.in_cache = True
                    count += 1
            else: # item does not exist yet - create it and insert to MRU and cache
                FP_item = FPItem(F, in_cache=True)
                memory[1].append(FP_item)
                count += 1
                FP_dict[F] = FP_item # important to keep the dictionary updates
            # now check if any evictions are needed as a result of the insertion:
            if count > cachesize: # cache is full
                victim = next(FP_victim for FP_victim in memory[1] if FP_victim.in_cache) # selects the cache item closest to LRU end
                victim.in_cache = False
                count -= 1
            if len(memory[1]) > 2 * cachesize:
                # remove the non-cached item that is closest to LRU end
                victim = next(FP_victim for FP_victim in memory[1] if not FP_victim.in_cache)
                memory[1].remove(victim)
                del FP_dict[victim.FP] # the dictionaries MUST match the memory content

            # Take care of replacing the LBA item:
            if L in LBA_dict: # item exist in memory
                LBA_item = LBA_dict[L]
                memory[0].remove(LBA_item)  # move item to MRU end
                memory[0].append(LBA_item)
            else:   # item does not exist yet - create it and insert to MRU
                LBA_item = LBAItem(L, F) # make new item point at F
                memory[0].append(LBA_item)
                LBA_dict[L] = LBA_item # important to keep the dictionary updated
            # Check if any evictions are needed in LBA list
            if len(memory[0]) > 2 * cachesize:
                victim = memory[0].pop()
                del LBA_dict[victim.LBA]

            # update the LBA item to point at the correct fingerprint
            LBA_item.FP = FP_item.FP


        if policy == 'HW4_LBA_ARC':
            # Take care of replacing the fingerprint:
            if F in FP_dict:  # item exists in memory
                FP_item = FP_dict[F]
                memory[1].remove(FP_item)   # move the item to MRU end
                memory[1].append(FP_item)
                if not FP_item.in_cache:    # item should also be put in cache
                    FP_item.in_cache = True
                    count += 1
            else: # item does not exist yet - create it and insert to MRU and cache
                FP_item = FPItem(F, in_cache=True)
                memory[1].append(FP_item)
                count += 1
                FP_dict[F] = FP_item # important to keep the dictionary updates
            # now check if any evictions are needed as a result of the insertion:
            if count > cachesize: # cache is full
                victim = next(FP_victim for FP_victim in memory[1] if FP_victim.in_cache) # selects the cache item closest to LRU end
                victim.in_cache = False
                count -= 1
            if len(memory[1]) > 2 * cachesize:
                # remove the non-cached item that is closest to LRU end
                victim = next(FP_victim for FP_victim in memory[1] if not FP_victim.in_cache)
                memory[1].remove(victim)
                del FP_dict[victim.FP] # the dictionaries MUST match the memory content

            # Take care of replacing the LBA item
            # Check if any evictions are needed in LBA list
            LBA_item, LBA_p = ARC(memory[0], LBA_p, count, LBAItem(L, 0))

            # update the LBA item to point at the correct fingerprint
            LBA_item.FP = FP_item.FP

        if policy == 'HW4':
            # Take care of replacing the fingerprint:
            # now check if any evictions are needed as a result of the insertion:
            FP_item, FP_p = ARC(memory[1], FP_p, count, FPItem(F, in_cache=True))

            # Take care of replacing the LBA item
            # Check if any evictions are needed in LBA list
            LBA_item, LBA_p = ARC(memory[0], LBA_p, count, LBAItem(L, 0))

            # update the LBA item to point at the correct fingerprint
            LBA_item.FP = FP_item.FP

        # if you fail this assertion, you have exceeded your cache space capacity.
        assert(check_mem_limit(memory, cachesize))
        assert(count <= cachesize)
        #assert(count == len([fp for fp in FP_dict.values() if fp.in_cache]))
        # it is recommended to run at least once with the above assertion
        # (but not all the time, since it increases the runtime greatly)

        if notrace is False:
            print(te)
    
print('')
print('FINALSTATS hits %d   misses %d   hitrate %.5f' % (hits, miss, (100.0*float(hits))/(float(hits)+float(miss))))
print('')
