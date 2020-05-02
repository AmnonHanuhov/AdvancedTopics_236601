from optparse import OptionParser
import os
import subprocess
import matplotlib.pyplot as plt
import numpy as np

fifo11 = []
lru11 = []
fifo12 = []
lru12 = []
fifo13 = []
lru13 = []
fifo14 = []
lru14 = []
with open('prxy_1.11.out', 'r') as file:
    for line in file:
        (fifo, lru) = line.split()
        fifo11.append(int(fifo))
        lru11.append(int(lru))
with open('prxy_1.12.out', 'r') as file:
    for line in file:
        (fifo, lru) = line.split()
        fifo12.append(int(fifo))
        lru12.append(int(lru))
with open('prxy_1.13.out', 'r') as file:
    for line in file:
        (fifo, lru) = line.split()
        fifo13.append(int(fifo))
        lru13.append(int(lru))
with open('prxy_1.14.out', 'r') as file:
    for line in file:
        (fifo, lru) = line.split()
        fifo14.append(int(fifo))
        lru14.append(int(lru))

fig, plots = plt.subplots(4)
fig.tight_layout()
plots[0].plot(fifo11, label='fifo')
plots[0].plot(lru11, label='lru')
plots[1].plot(fifo12, label='fifo')
plots[1].plot(lru12, label='lru')
plots[2].plot(fifo13, label='fifo')
plots[2].plot(lru13, label='lru')
plots[3].plot(fifo14, label='fifo')
plots[3].plot(lru14, label='lru')
plots[0].autoscale()
plots[0].legend()
plots[1].autoscale()
plots[1].legend()
plots[2].autoscale()
plots[2].legend()
plots[3].autoscale()
plots[3].legend()
plots[0].set_title('11')
plots[1].set_title('12')
plots[2].set_title('13')
plots[3].set_title('14')

# plot.set_title(trace)
# plot.set_yticks([y for y in range(0, 120, 20)])
# plot.set_yticklabels(['{}%'.format(y) for y in range(0, 120, 20)])
# plot.set_ylim(0, 100)
# plot.set_xticks(cache_sizes)
# plot.set_xticklabels(cache_sizes_labels)
# plot.set_xlim(12, 20)
# plot.autoscale()
# plot.legend()

plt.ioff()
plt.show()

