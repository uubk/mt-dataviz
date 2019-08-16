#!/usr/bin/env python3
import argparse
import bz2

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

parser = argparse.ArgumentParser(description='Plot gcd data file')
parser.add_argument('--inputBaseline', dest='inputBaseline', required=True,
                    help='Baseline data file')
parser.add_argument('--titleBaseline', dest='titleBaseline', required=True,
                    help='Baseline description')
parser.add_argument('--input', dest='input', nargs='+',
                    help='Input file to use')
parser.add_argument('--title', dest='title', nargs='+',
                    help='Title for input file')
parser.add_argument('--output', dest='output', required=True,
                    help='Output file prefix')
args = parser.parse_args()


def read_data(filename):
    if filename.endswith(".bz2"):
        with bz2.open(filename, "r") as input:
            data = input.read().decode('utf-8')
    else:
        with open(filename, "r") as input:
            data = input.read()
    return np.array(list(map(int, data.split('\n')[:-1])))


dataBaseline = read_data(args.inputBaseline)
titleBaseline = args.titleBaseline

dataRest = []
titleRest = []
for idx, filename in enumerate(args.input):
    data = read_data(filename)
    title = args.title[idx]
    dataRest.append(data)
    titleRest.append(title)
    print("Got {} datapoints".format(len(data)))

prefix = args.output
print("Got {} datapoints for baseline".format(len(dataBaseline)))

dataRest = [dataBaseline/x for x in dataRest]

# Sort all lists the same way
sortIdx = sorted(range(len(dataRest[0])), key=lambda k: dataRest[0][k])
dataRest = [x[sortIdx] for x in dataRest]

# Plot histogram
fig = plt.figure(figsize=[12, 4])
figGrid = plt.GridSpec(1, 24, wspace=0, hspace=0)
ax = fig.add_subplot(figGrid[0, 0:20])
plt.grid(b=True, which='major', axis='y', linewidth=0.2, color='grey', zorder=0)
#plt.grid(b=True, which='minor', axis='y', linewidth=0.2, color='grey', zorder=0)
plt.grid(b=True, which='major', axis='x', linewidth=0.2, color='grey', zorder=1)
ax.tick_params(axis='x', colors='black')
ax.tick_params(axis='y', colors='black')
plotRefs = []
for idx, data in enumerate(dataRest):
    plotRefs.append(ax.plot(data, label=titleRest[idx]))

plt.xlim(0)
legend = ax.legend(fontsize=14)
legend.get_frame().set_edgecolor('white')
plt.xlabel("Testcase", fontsize=14)
plt.ylabel("Speedup over arbitrary precision (GMP)", fontsize=12)
for idx, label in enumerate(ax.yaxis.get_ticklabels()):
    label.set_color('black')
    label.set_size(14)
for idx, label in enumerate(ax.xaxis.get_ticklabels()):
    label.set_color('black')
    label.set_size(14)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

ax2 = fig.add_subplot(figGrid[0, 21:])
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
ax2.spines["left"].set_visible(False)

colorize = lambda c: {"notch": True,
                  "patch_artist": True,
                 "boxprops": dict(facecolor=c, color=c),
            "capprops": dict(color=c),
            "whiskerprops": dict(color=c),
            "flierprops": dict(color=c, markeredgecolor=c),
            "medianprops": dict(color=c)}

for idx, data in enumerate(dataRest):
    ax2.boxplot(data, positions=[0.3 * idx], **colorize(plotRefs[idx][0]._color))
ax2.get_xaxis().set_visible(False)
ax2.tick_params(axis='y', colors='black')
ax2.grid(b=True, which='major', axis='y', linewidth=0.2, color='black', zorder=0)

#bins = np.array(range(0, max((int(max(data)))*5+1, 5), 1))/5
#ax.hist(data, bins=bins, align='left')
#plt.xlim(0.0, (max(data) + 0.2))
#xTicks = np.arange(0.0, (max(data)+0.2), 0.2)
#xTicks = np.insert(xTicks, 0, (int(max(data))+0.2))
#ax.set_xticks(xTicks)

plt.tight_layout()

for format in [".png", ".pdf"]:
    if format == ".pdf":
        ax.set_title("")
    plt.savefig(prefix + format, dpi=180)# extraArtists=extraArtists)

try:
    import mpld3
    mpld3.save_html(fig, prefix + ".html")
except ImportError:
    pass
