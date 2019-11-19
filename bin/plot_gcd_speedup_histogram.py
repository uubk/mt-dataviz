#!/bin/env python3
import argparse
import bz2

import numpy as np
import seaborn as sns
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
parser.add_argument('--isgcd', dest='isgcd', required=True,
                    help='Whether this is a GCD or a general speedup plot')

args = parser.parse_args()


def read_data(filename):
    if filename.endswith(".bz2"):
        with bz2.open(filename, "r") as input:
            data = input.read().decode('utf-8')
    else:
        with open(filename, "r") as input:
            data = input.read()
    return np.array(list(map(int, data.split('\n')[:-1])))

filename = args.inputA
dataA = read_data(args.inputA)
dataB = read_data(args.inputB)

prefix = args.output
print("Got {} and {} datapoints".format(len(dataA), len(dataB)))

data = dataA/dataB
# print(sum(data<1)/len(data))

sns.set_context('paper', font_scale=3)
# Plot histogram
fig, ax = plt.subplots(figsize=[18.5, 6])
ax.set_yscale("log", nonposy='clip')
# plt.grid(b=True, which='major', axis='y', linewidth=1, color='black', zorder=0)
#plt.grid(b=True, which='minor', axis='y', linewidth=0.2, color='grey', zorder=0)
# plt.grid(b=True, which='major', axis='x', linewidth=1, color='black', zorder=1)
# ax.tick_params(axis='x', colors='black')
# ax.tick_params(axis='y', colors='black')
if args.isgcd == "False":
    bins = np.array(range(0, max((int(max(data)))*5+1, 5), 1))/5
    ax.hist(data, bins=bins, align='left')
    plt.xlim(0.0, (max(data) + 0.2))
    xTicks = np.arange(0.0, (max(data)+0.2), 0.2)
    #xTicks = np.insert(xTicks, 0, (int(max(data))+0.2))
    ax.set_xticks(xTicks)
else:
    ax.hist(data, bins=range(int(min(data)), int(max(data)) + 1, 1), align='left')
    (_, right) = plt.xlim()
    plt.xlim(2, right)
    xTicks = np.arange(10, right, 10)
    # xTicks = np.insert(xTicks, 0, 2)
    ax.set_xticks(xTicks)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    med = np.median(data)
    print(med)
    ax.axvline(med, linewidth=2, color='black')
    plt.annotate('median', (med + 0.1, 10**6 * 5), (med + 1, 10**7),
                 arrowprops={
                     'width': 1.5,
                     'headwidth': 6,
                     'headlength': 6,
                     'color': 'black'
                 },
                 fontsize=26)
    pc75= np.percentile(data, 75)
    ax.axvline(pc75, linewidth=2, color='black')
    plt.annotate('75pc', (pc75 + 0.1, 10**6 * 1), (pc75 + 1.5, 10**6 * 3),
                 arrowprops={
                     'width': 1.5,
                     'headwidth': 6,
                     'headlength': 6,
                     'color': 'black'
                 },
                 fontsize=26)
    pc25= np.percentile(data, 25)
    ax.axvline(pc25, linewidth=2, color='black')
    plt.annotate('25pc', (pc25 - 0.1, 10**6 * 5), (pc25 - 3, 10**7),
                 arrowprops={
                     'width': 1.5,
                     'headwidth': 6,
                     'headlength': 6,
                     'color': 'black'
                 },
                 fontsize=26)



    plt.xlim(int(min(data)), 45)

    axins = inset_axes(ax, width='45%', height='60%')
    axins.set_yscale("log", nonposy='clip')
    lodata = data[data <= 2]
    axins.hist(lodata, align='left')

plt.tight_layout()

for format in [".png", ".pdf"]:
    if format == ".pdf":
        ax.set_title("")
        ax.set_ylabel("Count")
        ax.set_xlabel("Speedup")
    plt.savefig(prefix + format, bbox_inches='tight',
                dpi=180)  # extraArtists=extraArtists)

try:
    import mpld3
    mpld3.save_html(fig, prefix + ".html")
except ImportError:
    pass
