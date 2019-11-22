#!/usr/bin/env python3
import argparse

import numpy as np
import seaborn as sns
from matplotlib.ticker import MultipleLocator
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(description='Plot gcd data file')
parser.add_argument('--inputA', dest='inputA', required=True,
                    help='Configures which file to plot')
parser.add_argument('--inputB', dest='inputB', required=True,
                    help='Configures which file to plot')
parser.add_argument('--output', dest='output', required=True,
                    help='Configures prefix to plot to')

args = parser.parse_args()
filenameA = args.inputA
filenameB = args.inputB
output = args.output

print ("loading data")
dataA = []
dataB = []

# 10 repetitions, ns to us
factor = 1000 * 10

with open(filenameA, 'r') as file:
    line = file.readline()
    while line:
        val = int(line.strip()) / factor
        dataA.append(val)
        line = file.readline()

with open(filenameB, 'r') as file:
    line = file.readline()
    while line:
        val = int(line.strip()) / factor
        dataB.append(val)
        line = file.readline()


print("Data loaded")

sns.set(rc={"xtick.bottom" : True, "ytick.left" : True})
sns.set_style("whitegrid", rc={"xtick.bottom" : True, "ytick.left" : True})
sns.set_context('paper', font_scale=3, rc={"xtick.bottom" : True, "ytick.left" : True})
fig, axes = plt.subplots(2, 1, sharey="all", sharex="none")

bins = np.arange(5000, step=100)
bins = np.append(bins, [10000000])
ax = sns.distplot(dataA, bins=bins, kde=False, color=(0.12, 0.57, 0.71), ax=axes[0])
ax2 = sns.distplot(dataB, bins=bins, kde=False, color=(0.38, 0.79, 0.45), ax=axes[1])

ax.set(xlim=(0, 5000))
ax2.set(xlim=(0, 5000))
#ax2.set(xlim=(126, 128))
#ax.spines['right'].set_visible(False)
#ax2.spines['left'].set_visible(False)
ax.yaxis.tick_left()
#ax2.yaxis.tick_right()

ax.set_yscale('log')
ax.set_ylabel('Count\n(GMP)')
ax.set_xlabel('time (us)')
ax2.set_yscale('log')
ax2.set_ylabel('Count\n(libint)')
ax2.set_xlabel('time (us)')
ax.xaxis.set_minor_locator(MultipleLocator(500))
ax.tick_params(which='minor', length=8)
ax.tick_params(which='major', length=6)
ax2.xaxis.set_minor_locator(MultipleLocator(500))
ax2.tick_params(which='minor', length=8)
ax2.tick_params(which='major', length=6)

fig.set_size_inches(18.5, 10)
fig.tight_layout()

# Only edit the labels _now_
fig.canvas.draw()
labels = [item.get_text() for item in ax.get_xticklabels(which='both')]
labels[-1] = "longer"
ax.set_xticklabels(labels)
fig.canvas.draw()
labels = [item.get_text() for item in ax2.get_xticklabels(which='both')]
labels[-1] = "longer"


plt.savefig(output, bbox_inches='tight')