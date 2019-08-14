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


prefix = args.output
print("Got {}, {}, {} and {} datapoints".format(len(dataBaseline), len(dataIMath), len(dataMulti), len(dataLIFix)))

speedupImath = dataBaseline/dataIMath
speedupMulti = dataBaseline/dataMulti
speedupLIFix = dataBaseline/dataLIFix

# Sort all lists the same way
sortIdx = sorted(range(len(speedupLIFix)), key=lambda k: speedupLIFix[k])
speedupImath = speedupImath[sortIdx]
speedupMulti = speedupMulti[sortIdx]
speedupLIFix = speedupLIFix[sortIdx]

# Plot histogram
fig, ax = plt.subplots(figsize=[12, 4])
plt.grid(b=True, which='major', axis='y', linewidth=0.2, color='grey', zorder=0)
#plt.grid(b=True, which='minor', axis='y', linewidth=0.2, color='grey', zorder=0)
plt.grid(b=True, which='major', axis='x', linewidth=0.2, color='grey', zorder=1)
ax.tick_params(axis='x', colors='black')
ax.tick_params(axis='y', colors='black')
plt.plot(speedupImath, label="IMath")
plt.plot(speedupMulti, label="ISL hand-vectorized")
plt.plot(speedupLIFix, label="libint")
plt.xlim(0)
plt.legend()
plt.xlabel("Testcase")
plt.ylabel("Speedup")
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
        ax.set_ylabel("")
    plt.savefig(prefix + format, dpi=180)# extraArtists=extraArtists)

try:
    import mpld3
    mpld3.save_html(fig, prefix + ".html")
except ImportError:
    pass
