#!/bin/env python3
import argparse
import bz2

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

parser = argparse.ArgumentParser(description='Plot gcd data file')
parser.add_argument('--inputGMP', dest='inputGMP', required=True,
                    help='inputGMP')
parser.add_argument('--inputIMath', dest='IMath', required=True,
                    help='IMath')
parser.add_argument('--inputMulti', dest='Multi', required=True,
                    help='Multi')
parser.add_argument('--inputLIFix', dest='LIFix', required=True,
                    help='LIFix')
parser.add_argument('--inputLITPx', dest='LITP', required=True,
                    help='LITP')
parser.add_argument('--output', dest='output', required=True,
                    help='Configures prefix to plot to')

args = parser.parse_args()


def read_data(filename):
    if filename.endswith(".bz2"):
        with bz2.open(filename, "r") as input:
            data = input.read().decode('utf-8')
    else:
        with open(filename, "r") as input:
            data = input.read()
    return np.array(list(map(int, data.split('\n')[:-1])))


dataBaseline = read_data(args.inputGMP)
dataIMath = read_data(args.IMath)
dataMulti = read_data(args.Multi)
dataLIFix = read_data(args.LIFix)
dataLITP = read_data(args.LITP)


prefix = args.output
print("Got {}, {}, {} and {} datapoints".format(len(dataBaseline), len(dataIMath), len(dataMulti), len(dataLIFix)))

speedupImath = dataBaseline/dataIMath
speedupMulti = dataBaseline/dataMulti
speedupLIFix = dataBaseline/dataLIFix
speedupLITP = dataBaseline/dataLITP

# Sort all lists the same way
sortIdx = sorted(range(len(speedupLIFix)), key=lambda k: speedupLIFix[k])
speedupImath = speedupImath[sortIdx]
speedupMulti = speedupMulti[sortIdx]
speedupLIFix = speedupLIFix[sortIdx]
speedupLITP = speedupLITP[sortIdx]

# Plot histogram
fig = plt.figure(figsize=[12, 4])
figGrid = plt.GridSpec(1, 24, wspace=0, hspace=0)
ax = fig.add_subplot(figGrid[0, 0:20])
plt.grid(b=True, which='major', axis='y', linewidth=0.2, color='grey', zorder=0)
#plt.grid(b=True, which='minor', axis='y', linewidth=0.2, color='grey', zorder=0)
plt.grid(b=True, which='major', axis='x', linewidth=0.2, color='grey', zorder=1)
ax.tick_params(axis='x', colors='black')
ax.tick_params(axis='y', colors='black')
imath = ax.plot(speedupImath, label="Element-granularity transprecision")
isl = ax.plot(speedupMulti, label="Matrix-granularity transprecison (manual)")
libint = ax.plot(speedupLIFix, label="Fixed type")
libint_tp = ax.plot(speedupLITP, label="Matrix-granularity transprecision (automatic)")
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

ax2 = fig.add_subplot(figGrid[0, 21:])

colorize = lambda c: {"notch": True,
                  "patch_artist": True,
                 "boxprops": dict(facecolor=c, color=c),
            "capprops": dict(color=c),
            "whiskerprops": dict(color=c),
            "flierprops": dict(color=c, markeredgecolor=c),
            "medianprops": dict(color=c)}

ax2.boxplot(speedupImath, positions=[0.0], **colorize(imath[0]._color))
ax2.boxplot(speedupMulti, positions=[0.3], **colorize(isl[0]._color))
ax2.boxplot(speedupLIFix, positions=[0.6], **colorize(libint[0]._color))
ax2.boxplot(speedupLITP, positions=[0.9], **colorize(libint_tp[0]._color))
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
