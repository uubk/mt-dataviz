import matplotlib.pyplot as plt
import re


class DuplicateDataException(Exception):
    pass


class Plotter():
    def __init__(self, data, assignment, axis):
        self._data = data
        self._assignment = assignment
        self._axis = axis

    def groupData(self):
        for i in range(len(self._data)):
            data = self._data[i]
            experimentsToUse = self._assignment[i]
            experimentData = [[]] * len(self._axis)
            for experimentRegex in experimentsToUse:
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
            print (experimentData)

    def plot(self):
        fig = plt.figure()  # an empty figure with no axes