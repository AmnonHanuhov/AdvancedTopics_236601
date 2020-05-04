from optparse import OptionParser
import os
from multiprocessing import Pool
import subprocess
import matplotlib.pyplot as plt
import numpy as np

output_filename = "results/hw2_cache_splited.log"
directory = os.fsencode("./traces/")
cache_sizes = [size for size in range(12, 21)]
cache_sizes_blocks = [2**size for size in range(12, 21)]
cache_sizes_labels = [str(size) for size in range(12, 21)]

def plot_log():
     data = {}
     with open(output_filename, 'r') as file:
          for line in file:
               (trace, policy, cache_size, misses, hits, hitrate) = line.split()
               if not trace in data:
                    data[trace] = {}
               if not policy in data[trace]:
                    data[trace][policy] = []
               data[trace][policy].append((int(cache_size), float(hitrate)))

     with open('results/cache_splited.log', 'r') as file:
          for line in file:
               (trace, policy, cache_size, misses, hits, hitrate) = line.split()
               if policy == 'MRU':
                    continue
               if not trace in data:
                    data[trace] = {}
               if not policy in data[trace]:
                    data[trace][policy] = []
               data[trace][policy].append((int(cache_size), float(hitrate)))

     for trace, val in data.items():
          for policy, sizes_hitrates_list in val.items():
               l = sorted(sizes_hitrates_list, key=lambda tup: tup[0])
               val[policy] = []
               for tup in l:
                    val[policy].append(tup[1])

     # Finaly export figure to png
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
          # plot.autoscale()
          plot.legend()

     plt.autoscale()
     plt.delaxes()
     plt.ioff()
     plt.show()


def commands():
     result = []
     with open(output_filename, "a") as logfile:
          for file in os.listdir(directory):
               filename = os.fsdecode(file)
               if filename.endswith(".trace"):
                    for policy in ["HW2", ]:
                         for cache_size in cache_sizes_blocks:
                              bashCommand = \
                                   "python paging-policy.py -f traces/{} --policy={} --cachesize={} -N -S".format(filename, policy, cache_size)
                              result.append((bashCommand, filename, cache_size))
     return result

def run_trace(tup):
     bashCommand, filename, cache_size = tup
     print(bashCommand)
     completed_process = subprocess.run(bashCommand.split(), capture_output=True)
     output_str = completed_process.stdout.decode("utf-8")
     for line in iter(output_str.splitlines()):
          if line.startswith('FINALSTATS'):
               (hits, misses, hitrate)  = line.split()[2:7:2]
               break
     output_str = '{} HW2 {} {} {} {}'.format(filename, cache_size, hits, misses, hitrate)
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

     plot_log()

