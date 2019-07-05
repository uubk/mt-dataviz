import matplotlib.pyplot as plt
import numpy as np
from functools import reduce
import re

from matplotlib.ticker import MaxNLocator


class DuplicateDataException(Exception):
    pass


class Plotter():
    def __init__(self, data, assignment, axis, lineplot, perAxisOptions, logplot, zero):
        self._data = data
        self._assignment = assignment
        self._axis = axis
        self._groups = []
        self.formats = [".png", ".pdf"]
        self._history = False
        self._speedup = False
        self._diff = False
        self._perAxisOptions = perAxisOptions
        self.bars = not lineplot
        self._logplot = logplot
        self._zero = zero

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

    def groupToDiff(self):
        self._diff = True

        def unifyGroups(groupA, groupB):
            groupB["data"] = [(groupA["data"][index][0]/x[0], 0) for index, x in enumerate(groupB["data"])]
            return groupB

        self._groups = [unifyGroups(grouptuple[0], grouptuple[1]) for grouptuple in
                        zip(self._groups[::2], self._groups[1::2])]

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
        minWidth = index-individualWidth*(numExps/2)
        index = list(index)

        fig, ax = plt.subplots(figsize=(5, 8))
        if self._logplot:
            ax.set_yscale("log", nonposy='clip')

        legendGroups = {}
        argumentGroups = {}
        for idx, group in enumerate(self._groups):
            plotOptions = {
                "yerr": [x[1] for x in group['data']],
                "label": group['label'],
                "zorder":  3,
                #"fontsize": 20
            }

            name = group['label']
            legendGroup = None
            argumentGroup = None
            if name in self._perAxisOptions:
                for key, value in self._perAxisOptions[name].items():
                    if key == "legendGroup":
                        if not value in legendGroups:
                            legendGroups[value] = []
                        legendGroup = value
                    elif key == "argGroup":
                        if not value in argumentGroups:
                            argumentGroups[value] = []
                        argumentGroup = value
                    else:
                        plotOptions[key] = value

            if legendGroup:
                # remove label
                plotOptions.pop('label', None)

            if "skip" not in plotOptions:
                if self.bars:
                    currentPlot = ax.bar(list(minWidth + individualWidth*idx), [x[0] for x in group['data']], individualWidth, **plotOptions)
                else:
                    if "marker" not in plotOptions:
                        plotOptions["marker"] = "."
                    currentPlot = ax.errorbar(index, [x[0] for x in group['data']], **plotOptions)

                if legendGroup:
                    legendGroups[legendGroup].append(currentPlot)
                if argumentGroup:
                    argumentGroups[argumentGroup].append(currentPlot)


        if self._speedup:
            ax.set_ylabel('Speedup', fontsize=20)
        else:
            ax.set_ylabel('Time (ns)', fontsize=20)
        ax.set_title(title)

        if numberOfExperiments > 5 and ":" in xLegends[0]:
            plt.xticks(rotation=90)
        ax.set_xticks(index)
        ax.set_xticklabels(xLegends, fontsize=20)
        extraArtists = []
        if legendGroups:
            # Legend group
            names = []
            items = []
            for name, axes in legendGroups.items():
                if len(axes) < 1:
                    continue
                names.append(name)
                items.append(axes[0])
            legend = plt.legend(items, names, loc=3, fontsize=14, bbox_to_anchor=(0., 1.02, 1., .102), ncol=2, mode="expand", borderaxespad=0.)
            plt.gca().add_artist(legend)
            extraArtists.append(legend)
            # Argument group
            names = []
            items = []
            for name, axes in argumentGroups.items():
                if len(axes) < 1:
                    continue
                names.append(name)
                items.append(axes[0])
            legend = plt.legend(items, names, loc=2, fontsize=14)
            plt.gca().add_artist(legend)
            extraArtists.append(legend)
        else:
            ax.legend(fontsize=14)

        plt.grid(b=True, which='major', axis='y', linewidth=0.3, color='grey', zorder=0)
        plt.grid(b=True, which='minor', axis='y', linewidth=0.2, color='lightgrey')
        ax.tick_params(axis='x', colors='grey')
        ax.tick_params(axis='y', colors='grey')
        for idx, label in enumerate(ax.xaxis.get_ticklabels()):
            xValue = xLegends[idx]
            try:
                intVal = int(xValue)
                if intVal % 8 != 0:
                    label.set_visible(False)
                else:
                    label.set_color('black')
            except ValueError:
                label.set_color('black')
        for idx, label in enumerate(ax.yaxis.get_ticklabels()):
            label.set_color('black')
            label.set_size(14)

        if self._zero:
            ax.set_ylim(ymin=0)

        for format in self.formats:
            if format == ".pdf":
                ax.set_title("")
                ax.set_ylabel("")
            plt.savefig(prefix + format, dpi=180, extraArtists=extraArtists)

        try:
            import mpld3
            mpld3.save_html(fig, prefix + ".html")
        except ImportError:
            pass
