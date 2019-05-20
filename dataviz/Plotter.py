import matplotlib.pyplot as plt
import numpy as np
from functools import reduce
import re


class DuplicateDataException(Exception):
    pass


class Plotter():
    def __init__(self, data, assignment, axis):
        self._data = data
        self._assignment = assignment
        self._axis = axis
        self._groups = []
        self.formats = [".png", ".eps"]

    def groupData(self):
        for i in range(len(self._data)):
            data = self._data[i]
            experimentsToUse = self._assignment[i]

            for (experimentRegex, experimentLabel) in experimentsToUse:
                experimentData = [[] for _ in range(len(self._axis))]
                for someExperimentName in data:
                    if re.match(experimentRegex, someExperimentName) is not None:
                        experiment = data[someExperimentName]
                        for idx, elem in enumerate(self._axis):
                            matching = True
                            for key, value in elem.items():
                                if key not in experiment['parameters'] or experiment['parameters'][key] != value:
                                    matching = False
                                    break
                            if matching:
                                if len(experimentData[idx]) != 0:
                                    raise DuplicateDataException("Index " + str(idx) + " was already populated!")
                                experimentData[idx] = experiment['data']

                # Map experiment data to axis
                experimentData = [[y.delta for y in x] for x in experimentData]
                experimentData = [(np.mean(x), np.std(x)) for x in experimentData]
                self._groups.append({
                    "label": experimentLabel,
                    "data": experimentData,
                })

    def plot(self, title, prefix):
        # We're plotting different experiments. Figure out which parameters change from run to run
        numberOfExperiments = len(self._groups[0]['data'])
        mask = {}
        values = {}
        for details in self._axis:
            for key, value in details.items():
                if key not in mask:
                    mask[key] = False
                    values[key] = value
                else:
                    if values[key] != value:
                        mask[key] = True
        xLegends = [[] for _ in range(numberOfExperiments)]
        for key, changes in mask.items():
            if changes:
                for idx, details in enumerate(self._axis):
                    value = details[key]
                    list = xLegends[idx]
                    list.append(key + ": " + value + " ")
        xLegends = [reduce((lambda x, y: x + "\n" + y), x).strip() for x in xLegends]

        index = np.arange(len(self._groups[0]['data']))
        width = 0.4
        numExps = len(self._groups)
        individualWidth = width/numExps
        minWidth = index-individualWidth/2

        fig, ax = plt.subplots()
        for idx, group in enumerate(self._groups):
            bars = ax.bar(minWidth + individualWidth*idx, [x[0] for x in group['data']], individualWidth,
                          yerr=[x[1] for x in group['data']], label=group['label'])

        ax.set_ylabel('Time (ns)')
        ax.set_title(title)
        ax.set_xticks(index)
        ax.set_xticklabels(xLegends)
        ax.legend()
        fig.tight_layout()

        for format in self.formats:
            plt.savefig(prefix + format, dpi=180)
