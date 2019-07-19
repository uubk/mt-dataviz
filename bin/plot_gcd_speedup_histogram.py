#!/bin/env python3
import argparse
import bz2

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

parser = argparse.ArgumentParser(description='Plot gcd data file')
parser.add_argument('--inputA', dest='inputA', required=True,
                    help='Configures which file to plot')
parser.add_argument('--inputB', dest='inputB', required=True,
                    help='Configures which file to plot')
parser.add_argument('--output', dest='output', required=True,
                    help='Configures prefix to plot to')

args = parser.parse_args()


def read_data(filename):
    if filename.endswith(".bz2"):
        with bz2.open(filename, "r") as input:
            data = input.read().decode('utf-8')
    else:
        with open(args.input, "r") as input:
            data = input.read()
    return np.array(list(map(int, data.split('\n')[:-1])))

filename = args.inputA
dataA = read_data(args.inputA);
dataB = read_data(args.inputB);

prefix = args.output
print("Got {} and {} datapoints".format(len(dataA), len(dataB)))

data = dataA/dataB
print(sum(data<1)/len(data))

# Plot histogram
fig, ax = plt.subplots(figsize=[12, 4])
ax.set_yscale("log", nonposy='clip')
# plt.grid(b=True, which='major', axis='y', linewidth=1, color='black', zorder=0)
#plt.grid(b=True, which='minor', axis='y', linewidth=0.2, color='grey', zorder=0)
# plt.grid(b=True, which='major', axis='x', linewidth=1, color='black', zorder=1)
ax.tick_params(axis='x', colors='black')
ax.tick_params(axis='y', colors='black')
ax.hist(data, bins=range(int(min(data)), int(max(data)) + 1, 1), align='left')
(_, right) = plt.xlim()
plt.xlim(2, right)
xTicks = np.arange(10, right, 10)
xTicks = np.insert(xTicks, 0, 2)
ax.set_xticks(xTicks)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
med = np.median(data)
print(med)
ax.axvline(med, linewidth=2, color='black')
plt.annotate('median', (med, 10**6 * 5), (med + 2, 10**6 * 9),
             arrowprops={
                 'width': 1.5,
                 'headwidth': 4,
                 'headlength': 4,
                 'color': 'black'
             })
pc75= np.percentile(data, 75)
ax.axvline(pc75, linewidth=2, color='black')
plt.annotate('75th pc', (pc75, 10**6 * 5), (pc75 + 2, 10**6 * 9),
             arrowprops={
                 'width': 1.5,
                 'headwidth': 4,
                 'headlength': 4,
                 'color': 'black'
             })
pc25= np.percentile(data, 25)
ax.axvline(pc25, linewidth=2, color='black')
plt.annotate('25th pc', (pc25, 10**6 * 5), (pc25 - 3, 10**6 * 9),
             arrowprops={
                 'width': 1.5,
                 'headwidth': 4,
                 'headlength': 4,
                 'color': 'black'
             })



plt.xlim(int(min(data)), 45)

axins = inset_axes(ax, width='45%', height='60%')
axins.set_yscale("log", nonposy='clip')
lodata = data[data <= 2]
axins.hist(lodata, align='left')
plt.tight_layout()


for format in [".png", ".pdf"]:
    if format == ".pdf":
        ax.set_title("")
        ax.set_ylabel("")
    plt.savefig(prefix + format, dpi=180)# extraArtists=extraArtists)

try:
    import mpld3
    mpld3.save_html(fig, prefix + ".html")
except ImportError:
    pass
