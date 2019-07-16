import argparse
import bz2

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

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

# Plot histogram
fig, ax = plt.subplots(figsize=[12, 4])
ax.set_yscale("log", nonposy='clip')
plt.grid(b=True, which='major', axis='y', linewidth=1, color='black', zorder=0)
#plt.grid(b=True, which='minor', axis='y', linewidth=0.2, color='grey', zorder=0)
plt.grid(b=True, which='major', axis='x', linewidth=1, color='black', zorder=1)
ax.tick_params(axis='x', colors='black')
ax.tick_params(axis='y', colors='black')
maximum = max(data)/8
maximum = int(maximum)
ax.hist(data, bins=range(min(data), maximum, 1), align='left')
(_, right) = plt.xlim()
plt.xlim(2, right)
xTicks = np.arange(10, right, 20)
xTicks = np.insert(xTicks, 0, 2)
ax.set_xticks(xTicks)

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
