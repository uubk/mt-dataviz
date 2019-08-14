import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from functools import reduce
import re

from matplotlib import cm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


# Ref: https://stackoverflow.com/a/20528097
def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
    '''
    Function to offset the "center" of a colormap. Useful for
    data with a negative min and positive max and you want the
    middle of the colormap's dynamic range to be at zero.

    Input
    -----
      cmap : The matplotlib colormap to be altered
      start : Offset from lowest point in the colormap's range.
          Defaults to 0.0 (no lower offset). Should be between
          0.0 and `midpoint`.
      midpoint : The new center of the colormap. Defaults to
          0.5 (no shift). Should be between 0.0 and 1.0. In
          general, this should be  1 - vmax / (vmax + abs(vmin))
          For example if your data range from -15.0 to +5.0 and
          you want the center of the colormap at 0.0, `midpoint`
          should be set to  1 - 5/(5 + 15)) or 0.75
      stop : Offset from highest point in the colormap's range.
          Defaults to 1.0 (no upper offset). Should be between
          `midpoint` and 1.0.
    '''
    cdict = {
        'red': [],
        'green': [],
        'blue': [],
        'alpha': []
    }

    # regular index to compute the colors
    reg_index = np.linspace(start, stop, 257)

    # shifted index to match the data
    shift_index = np.hstack([
        np.linspace(0.0, midpoint, 128, endpoint=False),
        np.linspace(midpoint, 1.0, 129, endpoint=True)
    ])

    for ri, si in zip(reg_index, shift_index):
        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    newcmap = matplotlib.colors.LinearSegmentedColormap(name, cdict)
    plt.register_cmap(cmap=newcmap)

    return newcmap


class DuplicateDataException(Exception):
    pass


class WrongDataShapeException(Exception):
    pass


class Plotter():
    def __init__(self, data, assignment, axis, lineplot, perAxisOptions, logplot, zero, autoYScale):
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
        self._autoYScale = autoYScale

    def groupData(self):
        for i in range(len(self._data)):
            data = self._data[i]
            experimentsToUse = self._assignment[i]

            for (experimentRegex, experimentLabel) in experimentsToUse:
                if len(self._axis) > 20:
                    self._axis = [self._axis]
                for _, axisGroup in enumerate(self._axis):
                    experimentData = [[] for _ in range(len(axisGroup))]
                    experiment = None
                    for someExperimentName in data:
                        if re.match(experimentRegex, someExperimentName) is not None:
                            experiment = data[someExperimentName]
                            for idx, elem in enumerate(axisGroup):
                                matching = True
                                for key, value in elem.items():
                                    if key not in experiment['parameters'] or experiment['parameters'][key] != value:
                                        matching = False
                                        break
                                if matching:
                                    if len(experimentData[idx]) != 0:
                                        raise DuplicateDataException("Index " + str(idx) + " was already populated!")
                                    experimentData[idx] = experiment['data']

                    if experiment is not None:
                        # Map experiment data to axis
                        experimentData = [[y.delta for y in x] for x in experimentData]
                        experimentData = [(np.mean(x), np.std(x)) for x in experimentData]
                        if not math.isnan(experimentData[0][0]):
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
            groupB["data"] = [(1-groupA["data"][index][0]/x[0], 0) for index, x in enumerate(groupB["data"])]
            return groupB

        self._groups = [unifyGroups(grouptuple[0], grouptuple[1]) for grouptuple in
                        zip(self._groups[::2], self._groups[1::2])]

    def groupToDiffSpeedup(self):
        self._diff = True
        self._speedup = True

        def unifyGroups(groupA, groupB):
            groupB["data"] = [(groupA["data"][index][0]/x[0], 0) for index, x in enumerate(groupB["data"])]
            return groupB

        self._groups = [unifyGroups(grouptuple[0], grouptuple[1]) for grouptuple in
                        zip(self._groups[::2], self._groups[1::2])]

    def plot(self, title, prefix, size):
        # We're plotting different experiments. Figure out which parameters change from run to run
        numberOfExperiments = len(self._groups[0]['data'])
        if not self._history:
            mask = {}
            values = {}
            for axisGroup in self._axis:
                for details in axisGroup:
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
                    for axisGroup in self._axis:
                        for idx, details in enumerate(axisGroup):
                            value = details[key]
                            xLegends[idx].append(key + ": " + value + " ")
            if len(xLegends[0]) == 1:
                xLegends = [re.sub(".*:", "", x[0]) for x in xLegends]
            else:
                xLegends = [reduce((lambda x, y: x + "\n" + y), x).strip() for x in xLegends]
        else:
            # Todo something useful
            xLegends = ["HEAD~" + str(numberOfExperiments-x-1) for x in range(numberOfExperiments)]

        convertedToUs = False
        if not self._speedup and not self._diff:
            # We're plotting time. Switch from ns to us when appropriate
            min = 1000
            max = 0
            for _, group in enumerate(self._groups):
                for (x, y) in group['data']:
                    if x > max:
                        max = x
                    if x < min:
                        min = x
            if min > 100 and max > 1000 and self._autoYScale:
                convertedToUs = True
                for _, group in enumerate(self._groups):
                    group['data'] = [(x/1000, y/1000) for (x, y) in group['data']]

        index = np.arange(len(self._groups[0]['data']))
        width = 0.4
        numExps = len(self._groups)
        individualWidth = width/numExps
        minWidth = index-individualWidth*(numExps/2)
        index = list(index)

        fig, ax = plt.subplots(figsize=size)

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
        elif self._diff:
            ax.set_ylabel('Slowdown (%)', fontsize=20)
        else:
            if convertedToUs:
                ax.set_ylabel('Time (us)', fontsize=20)
            else:
                ax.set_ylabel('Time (ns)', fontsize=20)
        ax.set_title(title)

        if self._logplot:
            ax.set_yscale("log", nonposy='clip')
            ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

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
            plt.savefig(prefix + format, dpi=180, extraArtists=extraArtists)

        try:
            import mpld3
            mpld3.save_html(fig, prefix + ".html")
        except ImportError:
            pass


    def plot2D(self, title, prefix, size, yScale):
        # Okay, so, 2D plots are tricky. We assume that one axis is the number of columns (N) and the other axis is
        # specified manually via mappings (M).
        # Matplotlib expects an NxM array, we have len(self._groups) = M and len(self._groups[whatever] = N
        # Let's use that to construct the array
        plotM = len (self._groups)
        plotN = len(self._groups[0]['data'])
        for group in self._groups:
            if len(group['data']) != plotN:
                raise WrongDataShapeException("All columns must have equal length")

        plotData = [[y[0] for y in x['data']] for x in self._groups]

        min = 1000
        max = 0
        for _, group in enumerate(self._groups):
            for (x, y) in group['data']:
                if x > max:
                    max = x
                if x < min:
                    min = x

        # We also need to figure out how to label stuff...
        numberOfExperiments = len(self._groups[0]['data'])
        numberOfGroups = len(self._groups)
        if not self._history:
            xLegends = [[] for _ in range(numberOfExperiments)]
            yLegends = [[] for _ in range(numberOfGroups)]
            for axisIdx, axisGroup in enumerate(self._axis):
                mask = {}
                values = {}
                for details in axisGroup:
                    for key, value in details.items():
                        if key not in mask:
                            mask[key] = False
                            values[key] = value
                        else:
                            if values[key] != value:
                                mask[key] = True
                for key, changes in mask.items():
                    if changes:
                        for idx, details in enumerate(axisGroup):
                            value = details[key]
                            strVal = key + ": " + value + " "
                            if strVal not in xLegends[idx]:
                                xLegends[idx].append(strVal)
                    else:
                        for idx, details in enumerate(axisGroup):
                            value = details[key]
                            strVal = key + ": " + value + " "
                            if strVal not in yLegends[axisIdx]:
                                yLegends[axisIdx].append(strVal)
            if len(xLegends[0]) == 1:
                xLegends = [re.sub(".*:", "", x[0]) for x in xLegends]
            else:
                xLegends = [reduce((lambda x, y: x + "\n" + y), x).strip() for x in xLegends]
            if len(yLegends[0]) == 1:
                # Special case: sparsity is percentage-based:
                if "sparsity" in yLegends[0][0]:
                    lut = {
                        1: "0%",
                        2: "50%",
                        4: "75%",
                        8: "87.5%",
                    }
                    yLegends = [lut[int(re.sub(".*:", "", x[0]))] for x in yLegends]
                else:
                    yLegends = [re.sub(".*:", "", x[0]) for x in yLegends]
            else:
                yLegends = [reduce((lambda x, y: x + "\n" + y), x).strip() for x in yLegends]
        else:
            # Todo something useful
            xLegends = ["HEAD~" + str(numberOfExperiments - x - 1) for x in range(numberOfExperiments)]

        fig, ax = plt.subplots(figsize=size)
        # We want to place 'white' at 1.0. This turns out to be quite involved
        # Range of values: [min, max]
        if min < 0:
            min = 0 # Cap min to zero

        if yScale != (1, 1):
            min = yScale[0]
            max = yScale[1]

        # We have an interval [min, max] with min >= 0. We now want to know how "long" the interval is and at which
        # percentage we find 1
        intervalLength = max - min
        positionOfOne = ((1-min) / (intervalLength/100)) / 100
        colorMap = shiftedColorMap(cm.RdBu, midpoint=positionOfOne)
        im = ax.imshow(plotData, cmap=colorMap, vmin=min, vmax=max)
        colorbarAxis = inset_axes(ax, loc='upper right', width='100%', height='10%', bbox_to_anchor=(0.01, 0.55, 1., 1.102), bbox_transform=ax.transAxes)
        plt.colorbar(im, orientation='horizontal', aspect=60, cax=colorbarAxis)
        xIdx = np.arange(6, len(xLegends)-6, step=8)
        xIdx = np.insert(xIdx, 0, 0)
        xLabels = list(filter(lambda x:
                              int(x.strip())%8 == 0,
                              xLegends))
        del xLabels[-1]
        xLabels.insert(0, xLegends[0])
        ax.set_xticks(xIdx)
        ax.set_xticks(np.arange(0.5, len(xLegends)+0.5, step=1), minor=True)
        ax.set_yticks(np.arange(len(yLegends)))
        ax.set_yticks(np.arange(-0.5, len(yLegends)+0.5, step=1), minor=True)
        ax.set_xticklabels(xLabels)
        ax.set_yticklabels(yLegends)
        plt.grid(b=True, which='minor', axis='y', linewidth=0.5, color='black', zorder=0)
        plt.grid(b=True, which='minor', axis='x', linewidth=0.5, color='black', zorder=0)
        #for i in range(plotM):
        #    for j in range(plotN):
        #        ax.text(j, i, "{0:.1f}".format(plotData[i][j]),
        #                       ha="center", va="center", color="black", size="5")

        if self._zero:
            ax.set_ylim(ymin=0)

        for format in self.formats:
            if format == ".pdf":
                ax.set_title("")
                ax.set_ylabel("")
            plt.savefig(prefix + format, dpi=180)

        try:
            import mpld3
            mpld3.save_html(fig, prefix + ".html")
        except ImportError:
            pass