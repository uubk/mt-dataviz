import json
import re
from pandas import Timedelta


class ParserException(Exception):
    pass


class Parser:
    def __init__(self, file, defaults):
        self._file = file
        self._host = None
        self._date = None
        self._defaults = defaults
        self.benchmarks = {}

    def parse(self):
        with open(self._file, "r") as file:
            contents = file.read()
            obj = json.loads(contents)
            if "context" not in obj:
                raise ParserException("No context section in file, is this really a benchmark result?")
            self._host = obj["context"]["host_name"]
            self._date = obj["context"]["date"]
            for singleBenchmark in obj["benchmarks"]:
                if singleBenchmark["run_type"] == "aggregate":
                    continue
                name = singleBenchmark["name"]
                nameKey = name
                # Let's figure out the real name without parameters, shall we?
                parameters = {}
                # Step 1: Check for templated type (<> syntax)
                res = re.search("<.*>", name)
                if res is not None:
                    parameters['type'] = res.group().replace('<', '').replace('>', '')
                    name = re.sub("<.*>", "", name)

                # Step 1: Check for templated type (_/ syntax)
                res = re.search("_u?int[0-9]{1,3}/", name)
                if res is not None:
                    parameters['type'] = res.group().replace('_', '').replace('/', '')
                    # Leave the '/'!
                    name = name.replace("_" + parameters['type'], "")

                if "type" in parameters:
                    parameters['type'] = parameters['type'].replace("_t", "")

                # Step 2: Check for templated single argument (_/ syntax)
                res = re.search("/[0-9]{1,2}", name)
                if res is not None:
                    parameters['columns'] = res.group().replace('/', '')
                    # Leave the '/'!
                    name = name.replace("/" + parameters['columns'], "")

                if "type" in parameters:
                    parameters['type'] = parameters['type'].replace("_t", "")

                # Step 3: Chomp arguments
                res = re.search('/.*:.*(?=/|$)', name)
                if res is not None:
                    # We have parameters
                    res = res.group()
                    parameterPairs = res[1:].split('/')
                    for parameter in parameterPairs:
                        splitValue = parameter.split(':')
                        key = splitValue[0]
                        value = splitValue[1]
                        parameters[key] = value
                    name = name.replace(res, "")

                # Step 3: Apply defaults
                for key, value in self._defaults.items():
                    if key not in parameters:
                        parameters[key] = value

                if nameKey not in self.benchmarks:
                    self.benchmarks[nameKey] = {
                        'name': name,
                        'parameters': parameters,
                        'data': [],
                    }
                timeUnit = singleBenchmark["time_unit"]
                time = singleBenchmark["cpu_time"]
                self.benchmarks[nameKey]["data"].append(Timedelta(value=time, unit=timeUnit))