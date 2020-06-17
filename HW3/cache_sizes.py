from os import listdir
from os.path import isfile, join
import xml.etree.ElementTree as ET
from math import ceil

def cache_sizes():
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
            

def block_temp():
    onlyfiles = [f for f in listdir('./final_log/') if isfile(join('./final_log/', f)) and f.find('hotcold') != -1]
    d = {f:[0 for i in range(0, 6)] for f in onlyfiles}
    for trace in d.keys():
        root = ET.parse('./final_log/{}'.format(trace)).getroot()
        for i, type_tag in enumerate(root.findall('chip/plane/')):
            temp = int(float(type_tag.get('Average_page_temperature'))) - 1
            d[trace][temp] = d[trace][temp] + 1
    print(d)

block_temp()
