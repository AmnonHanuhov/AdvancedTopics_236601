from math import ceil
with open('sizes.csv') as fd:
    for i, line in enumerate(fd):
        if i == 0:
            continue

        trace, unique = line.split(',')
        for op in [0.05, 0.10, 0.15, 0.20]:
            blocks = ceil((int(unique)/(1-float(op)))/32)
            print('{}\top: {}, blocks: {}'.format(trace, op, blocks))
