Following are the major adjustments made for the exercise.
Take these into account while implementing your cache policy:

1)
In hw2_utils.py you can find two wrapper classes:
	TraceEntry - 	This class is similar to what you saw in hw1.
			you DON'T need to use it in your implementation,
			and it's purpose is helping with the trace file I/O.

	CacheEntry - 	This class is what goes into the cache memory
			(instead of just integers as in the original implementation).
			As stated in the assignment, objects of this class contain
			the LBA, ghost and metadata fields, which you may use for your
			algorithms.

2)
New memory structure:
Instead of using a single list for the cache memory, there are now two data structures:
	
	memory:		Instead of a single list, memory is now an array of 6 lists.
			(This is so you can use different lists for different purposes)

	mem_dict:	In order to provide fast lookup, This is a hash table data structure that
			reflects the memory state.

			mem_dict maps a pair of (LBA, ghost_bool) to (list_num, idx),
			where 	LBA is a given address of a cache entry,
				ghost_bool is True/False on whether the entry is a ghost.
			If the entry is in the main memory:
				(list_num, idx) are the index pair indicating in which memory list
 				and at which index the actual CacheEntry object is located.
			Here (LBA, ghost_bool) is a KEY, meaning there can be at most one non-ghsot entry and
			one ghost entry for every single LBA (you won't need more than that for your policies).

			NOTE: 	you must make sure that mem_dict indeed reflects the correct
				state of the memory at any given moment.
				(see examples in the implementation)

			This means:
				* When an entry enters memory, it's key must enter mem_dict.
				* When an entry leaves memory, it's key must be removed from mem_dict.
				* When an entry changes index or memory list, it's corresponding
				  value in mem_dict must be updated.
				* same for ghost entries (but with ghost_bool=True in the key)
				

3)
In paging-policy.py there are two new functions: find_entry and find_ghost.
These functions can be used for a simple lookup of a given CacheEntry object in the cache.
find_entry only looks for non-ghost entries, while find_ghost does the opposite.

The lookup is done in O(1) amortized time due to mem_dict, so it is recommended that you use
these methods in your implementation when such lookup is needed.

In order to use the functions, you must pass the memory structure and mem_dict, as well as the address (LBA) for lookup.
The return value is the desired cache entry's indices if it exists, or else NOT_FOUND (which is the tuple (-1, -1)).
(See examples in the implementation). 

4) 
New flags:
	-a (--addressfile) is now a mandatory flag - you must supply an input trace.
	-S (--split) - 	use this flag when running your code on traces which contain
			multi-block cache requests, as this flag makes the cache split every
			request into multiple single-block requests.
			If you wish to avoid the additional overhead of this process,
			it is recommended to use the supplied split_requests.py script
			in order split your multi-block trace one time only before running the
			paging-policy.py code without the -S flag.

NOTE: 	You DO NOT change the initial lookup of an entry in the cache.
	The implementation of your new eviction policy should only be activated in case
	of a miss in the given lookup algorithm (which simply uses find_entry).
