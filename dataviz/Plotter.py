import matplotlib.pyplot as plt
import numpy as np
from functools import reduce
import re


class DuplicateDataException(Exception):
    pass


class Plotter():
    def __init__(self, data, assignment, axis, lineplot):
        self._data = data
        self._assignment = assignment
        self._axis = axis
        self._groups = []
        self.formats = [".png", ".eps", ".pdf"]
        self._history = False
        self._speedup = False
        self.bars = not lineplot

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

    def groupDataByFile(self):
        self._history = True
        experiments = [[] for _ in range(len(self._assignment[0]))]
        # For each file
        for i in range(len(self._data)):
            data = self._data[i]
            experimentsToUse = self._assignment[0]
            # For each experiment in that file
            for index, (experimentRegex, experimentLabel) in enumerate(experimentsToUse):
                # experimentData = [[] for _ in range(len(self._axis))]
                foundOne = False
                for someExperimentName in data:
                    if re.match(experimentRegex, someExperimentName) is not None:
                        for idx, elem in enumerate(self._axis):
                            matching = True
                            experiment = data[someExperimentName]
                            for key, value in elem.items():
                                if key not in experiment['parameters'] or experiment['parameters'][key] != value:
                                    matching = False
                                    break
                            if matching:
                                if foundOne:
                                    raise DuplicateDataException("Already populated!")
                                # We're to use this experiment
                                dataArr = [x.delta for x in experiment['data']]
                                datapoint = (np.mean(dataArr), np.std(dataArr))
                                experiments[index].append(datapoint)
                                foundOne = True
                if not foundOne:
                    experiments[index].append((0, 0))
        for index, experiment in enumerate(experiments):
            self._groups.append({
                "label": self._assignment[0][index][1],
                "data": experiment
            })

    def groupToSpeedup(self):
        self._speedup = True
        reference = self._groups[0]["data"]
        for group in self._groups:
            group["data"] = [(reference[index][0]/x[0], 0) for index, x in enumerate(group["data"])]

    def plot(self, title, prefix):
        # We're plotting different experiments. Figure out which parameters change from run to run
        numberOfExperiments = len(self._groups[0]['data'])
        if not self._history:
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
                        xLegends[idx].append(key + ": " + value + " ")
            if len(xLegends[0]) == 1:
                xLegends = [re.sub(".*:", "", x[0]) for x in xLegends]
            else:
                xLegends = [reduce((lambda x, y: x + "\n" + y), x).strip() for x in xLegends]
        else:
            # Todo something useful
            xLegends = ["HEAD~" + str(numberOfExperiments-x-1) for x in range(numberOfExperiments)]

        index = np.arange(len(self._groups[0]['data']))
        width = 0.4
        numExps = len(self._groups)
        individualWidth = width/numExps
        minWidth = index-individualWidth/2
        index = list(index)

        fig, ax = plt.subplots()
        for idx, group in enumerate(self._groups):
            if self.bars:
                ax.bar(list(minWidth + individualWidth*idx), [x[0] for x in group['data']], individualWidth,
                          yerr=[x[1] for x in group['data']], label=group['label'], zorder=3)
            else:
                ax.errorbar(list(minWidth + individualWidth*idx), [x[0] for x in group['data']],
                          yerr=[x[1] for x in group['data']], label=group['label'], zorder=3, marker=".")
                #ax.plot(list(minWidth + individualWidth*idx), [x[0] for x in group['data']],
                #          label=group['label'], zorder=3)
                #ax.errorbar(list(minWidth + individualWidth*idx), [x[0] for x in group['data']],
                #          yerr=[x[1] for x in group['data']],)

        if self._speedup:
            ax.set_ylabel('Speedup')
        else:
            ax.set_ylabel('Time (ns)')
        ax.set_title(title)
        if numberOfExperiments > 5 and ":" in xLegends[0]:
            plt.xticks(rotation=90)
        ax.set_xticks(index)
        ax.set_xticklabels(xLegends, fontsize=8)
        ax.legend()
        plt.minorticks_on()
        plt.grid(b=True, which='major', axis='y', linewidth=0.2, color='black', zorder=0)
        plt.grid(b=True, which='minor', axis='y', linewidth=0.1, color='grey')
        fig.tight_layout()

        for format in self.formats:
            plt.savefig(prefix + format, dpi=180)

        try:
            import mpld3
            mpld3.save_html(fig, prefix + ".html")
        except ImportError:
            pass
