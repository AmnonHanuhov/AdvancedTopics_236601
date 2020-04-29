from optparse import OptionParser
import os
import subprocess
import matplotlib.pyplot as plt
import numpy as np

output_filename = "hw2_cache.log"
directory = os.fsencode("./traces/")
cache_sizes = [size for size in range(12, 21)]
cache_sizes_blocks = [2**size for size in range(12, 21)]
cache_sizes_labels = [str(size) for size in range(12, 21)]

def rerun_hw2_policy():
     with open(output_filename, "a") as logfile:
          for file in os.listdir(directory):
               if file != b'prxy_1.trace':
                    continue
               filename = os.fsdecode(file)
               if filename.endswith(".trace"):
                    for cache_size in cache_sizes_blocks:
                         bashCommand = \
                              "python paging-policy.py -f traces/{} --policy=HW2 --cachesize={} -N".format(filename, cache_size)
                         print(bashCommand)
                         completed_process = subprocess.run(bashCommand.split(), capture_output=True)
                         output_str = completed_process.stdout.decode("utf-8")
                         for line in iter(output_str.splitlines()):
                              if line.startswith('FINALSTATS'):
                                   (hits, misses, hitrate)  = line.split()[2:7:2]
                                   break
                         output_str = '{} HW2 {} {} {} {}'.format(filename, cache_size, hits, misses, hitrate)
                         print(output_str)
                         logfile.write(output_str+'\n')
                         logfile.flush()

if __name__ == '__main__':
     parser = OptionParser()
     parser.add_option('-r', '--rerun', default=False, action='store_true', dest='rerun')
     (options, args) = parser.parse_args()
     if options.rerun:
          rerun_hw2_policy()

     data = {}
     with open(output_filename, 'r') as file:
          for line in file:
               (trace, policy, cache_size, misses, hits, hitrate) = line.split()
               if not trace in data:
                    data[trace] = {}
               if not policy in data[trace]:
                    data[trace][policy] = []
               data[trace][policy].append(float(hitrate))

     with open('cache.log', 'r') as file:
          for line in file:
               (trace, policy, cache_size, misses, hits, hitrate) = line.split()
               if not trace in data:
                    data[trace] = {}
               if not policy in data[trace]:
                    data[trace][policy] = []
               data[trace][policy].append(float(hitrate))

     # Finaly export figure to png
     cols = int(len(data.keys()) / 2)
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

     plt.ioff()
     plt.show()
