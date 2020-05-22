from math import ceil
with open('sizes.csv') as fd:
    for i, line in enumerate(fd):
        if i == 0:
            continue

        trace, unique = line.split(',')
        for op in [0.10, 0.15, 0.20]:
            physical_pages = float(unique)/(1-float(op))
            blocks1 = ceil(physical_pages/32)
            blocks2 = ceil(float(unique)/32) + 12
            print('{}\top: {}, blocks: {}'.format(trace, op, max(blocks1, blocks2)))
            
