from optparse import OptionParser
import os
from multiprocessing import Pool
from collections import OrderedDict
import subprocess
import matplotlib.pyplot as plt
import numpy as np
from math import log

output_filename = "results/hw2_cache_splited_full.log"
output_filename2 = "results/hw2_cache_splited_full_.log"
output_filename3 = "results/Bar.csv"
directory = os.fsencode("./traces/short/")

# cache_sizes = [size for size in range(12, 21)]
# cache_sizes_blocks = [2**size for size in range(12, 21)]
# cache_sizes_labels = [str(size) for size in range(12, 21)]
cache_sizes = [size for size in range(11, 17)]
cache_sizes_blocks = [2**size for size in range(11, 17)]
cache_sizes_labels = [str(size) for size in range(11, 17)]

def plot_log():
     data = {}
     # create list for each [trace][policy]
     with open(output_filename, 'r') as file:
          for line in file:
               (trace, policy, cache_size, misses, hits, hitrate) = line.split()
               if not trace in data:
                    data[trace] = OrderedDict([("HW2",[]), ("LRU",[]), ("FIFO",[]), ("RAND",[])])
     with open(output_filename2, 'r') as file:
          for line in file:
               (trace, policy, cache_size, misses, hits, hitrate) = line.split()
               if not trace in data:
                    data[trace] = OrderedDict([("HW2",[]), ("LRU",[]), ("FIFO",[]), ("RAND",[])])
     # append to lists
     with open(output_filename, 'r') as file:
          for line in file:
               (trace, policy, cache_size, misses, hits, hitrate) = line.split()
               data[trace][policy].append((int(cache_size), float(hitrate)))
     # append to lists
     with open(output_filename2, 'r') as file:
          for line in file:
               (trace, policy, cache_size, misses, hits, hitrate) = line.split()
               if policy != 'MRU':
                    data[trace][policy].append((int(cache_size), float(hitrate)))
     # sort by cachesize
     for trace, val in data.items():
          for policy, sizes_hitrates_list in val.items():
               l = sorted(sizes_hitrates_list, key=lambda tup: tup[0])
               val[policy] = []
               for tup in l:
                    val[policy].append(tup[1])

                    
     # Finaly export figure to png
     # cols = 3
     cols = int((1+len(data.keys())) / 2)
     fig, plots = plt.subplots(2, cols)
     fig.tight_layout()
     for (i, (trace, d)) in enumerate(data.items()):
          plot = plots[int(i / cols)][int(i % cols)]
          for policy, hitrates in d.items():
               plot.plot(cache_sizes, hitrates, label=policy)

          plot.set_title(trace)
          # plot.set_yticks([y for y in range(0, 120, 20)])
          # plot.set_yticklabels(['{}%'.format(y) for y in range(0, 120, 20)])
          # plot.set_ylim(0, 100)
          plot.set_xticks(cache_sizes)
          plot.set_xticklabels(cache_sizes_labels)
          plot.set_xlim(12, 20)
          plot.set(xlabel='log2(cachesize)', ylabel='hitrate %')
          # plot.xlabel('log2(cachesize)')
          # plot.ylabel('hitrate %')
          # plot.autoscale()
          plot.legend()

     plt.autoscale()
     plt.delaxes();
     plt.ioff()
     plt.show()

def plot_log_new():
     data = {}
     # create list for each [trace][policy]
     with open(output_filename3, 'r') as file:
          for line in file:
               (trace, policy, cache_size, hitrate) = line.split(',')
               if not trace in data:
                    data[trace] = OrderedDict([("HW2",[]), ("LRU",[]), ("FIFO",[]), ("RAND",[])])
     # append to lists
     with open(output_filename3, 'r') as file:
          for line in file:
               (trace, policy, cache_size, hitrate) = line.split(',')
               data[trace][policy].append((int(cache_size), float(hitrate)))
     # sort by cachesize
     for trace, val in data.items():
          for policy, sizes_hitrates_list in val.items():
               l = sorted(sizes_hitrates_list, key=lambda tup: tup[0])
               val[policy] = []
               for tup in l:
                    val[policy].append(tup[1])
                    
     # Finaly export figure to png
     # cols = 3
     # cols = int((1+len(data.keys())) / 2)
     cols = 5
     fig, plots = plt.subplots(2, cols)
     fig.tight_layout()
     for (i, (trace, d)) in enumerate(data.items()):
          print(i, int(i / cols), int(i % cols))
          plot = plots[int(i / cols)][int(i % cols)]
          for policy, hitrates in d.items():
               plot.plot(cache_sizes, hitrates, label=policy)

          plot.set_title(trace)
          # plot.set_yticks([y for y in range(0, 120, 20)])
          # plot.set_yticklabels(['{}%'.format(y) for y in range(0, 120, 20)])
          # plot.set_ylim(0, 100)
          plot.set_xticks(cache_sizes)
          plot.set_xticklabels(cache_sizes_labels)
          plot.set_xlim(11, 16)
          plot.set(xlabel='log2(cachesize)', ylabel='hitrate %')
          # plot.xlabel('log2(cachesize)')
          # plot.ylabel('hitrate %')
          # plot.autoscale()
          plot.legend()

     plt.autoscale()
     # plt.delaxes();
     plt.ioff()
     plt.show()

def commands():
     result = []
     with open(output_filename, "a") as logfile:
          for file in os.listdir(directory):
               filename = os.fsdecode(file)
               if filename.endswith(".trace"):
                    for policy in ["HW2"]:
                         for cache_size in cache_sizes_blocks:
                              bashCommand = \
                                   "python paging-policy.py -f traces/short/{} --policy={} --cachesize={} -N -S".format(filename, policy, cache_size)
                              result.append((bashCommand, filename, cache_size, policy))
     return result

def run_trace(tup):
     bashCommand, filename, cache_size, policy = tup
     print(bashCommand)
     completed_process = subprocess.run(bashCommand.split(), capture_output=True)
     output_str = completed_process.stdout.decode("utf-8")
     for line in iter(output_str.splitlines()):
          if line.startswith('FINALSTATS'):
               (hits, misses, hitrate)  = line.split()[2:7:2]
               break
     for line in iter(completed_process.stderr.decode("utf-8").splitlines()):
          print(line)
     output_str = '{} {} {} {} {} {}'.format(filename, policy, cache_size, hits, misses, hitrate)
     print(output_str)
     with open(output_filename, "a") as logfile:
          logfile.write(output_str+'\n')
          logfile.flush()

if __name__ == '__main__':
     parser = OptionParser()
     parser.add_option('-r', '--rerun', default=False, action='store_true', dest='rerun')
     (options, args) = parser.parse_args()
     if options.rerun:
          with Pool(6) as p:
               bash_commands = commands()
               p.map(run_trace, bash_commands)

     plot_log_new()

