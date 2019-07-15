import argparse
import bz2

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

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

ax2 = ax.twinx()
n, bins, patches = ax.hist(data, bins=range(int(min(data)), int(max(data)) + 1, 1), align='left', cumulative=True, histtype='step', color='black', linewidth=2)
patches[0].set_xy(patches[0].get_xy()[:-1])
ax.spines['top'].set_visible(False)
ax2.spines['top'].set_visible(False)
plt.xlim(int(min(data)), int(max(data)))


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
