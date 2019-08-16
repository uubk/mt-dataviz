#!/bin/env python3
import argparse
import bz2

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import seaborn as sns

parser = argparse.ArgumentParser(description='Plot gcd data file')
parser.add_argument('--input', dest='input', required=True,
                    help='Configures which file to plot')
parser.add_argument('--output', dest='output', required=True,
                    help='Configures prefix to plot to')

args = parser.parse_args()
filename = args.input

data = []

if filename.endswith(".bz2"):
    with bz2.open(args.input, "r") as input:
        for line in input:
            data.append(int(line))
else:
    with open(args.input, "r") as input:
        for line in input:
            data.append(int(line))

prefix = args.output
print("Got {} datapoints".format(len(data)))

print(sum(data))
sns.set_context('paper', font_scale=3)
# Plot histogram
fig, ax = plt.subplots(figsize=[18.5, 4])
ax.set_yscale("log", nonposy='clip')
# ax.tick_params(axis='x', colors='black')
# ax.tick_params(axis='y', colors='black')
maximum = max(data)/8
maximum = int(maximum)
ax.hist(data, bins=range(min(data), maximum, 1), align='left')
plt.xlim(10, 470)
(_, right) = plt.xlim()
xTicks = np.arange(10, right, 30)
# xTicks = np.insert(xTicks, 0, 2)
ax.set_xticks(xTicks)
(bottom, _ ) = plt.ylim()
plt.ylim(bottom, 10**7)
fig = plt.gcf()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

median = np.median(data)
print(f'Median {median}')
ax.axvline(median, linewidth=2, color='black')
plt.annotate('median', (median + 1, 10**6 * 3), (median + 10, 10**6 * 6),
             arrowprops={
                 'width': 1.5,
                 'headwidth': 6,
                 'headlength': 6,
                 'color': 'black'
             },
             fontsize=26)

for format in [".png", ".pdf"]:
    if format == ".pdf":
        ax.set_xlabel("Runtime (cycles)")
        ax.set_ylabel("Count")
    plt.savefig(prefix + format, bbox_inches='tight', dpi=180)# extraArtists=extraArtists)

try:
    import mpld3
    mpld3.save_html(fig, prefix + ".html")
except ImportError:
    pass
