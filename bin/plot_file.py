from dataviz import Parser, Plotter
import argparse
import json

parser = argparse.ArgumentParser(description='Plot files according to config')
parser.add_argument('--config', dest='config', required=True,
                    help='Configures which files to plot')

args = parser.parse_args()
with open(args.config, "r") as cfgFile:
    config = json.loads(cfgFile.read())
    data = []
    for file in config['files']:
        parser = Parser(file, config['defaults'])
        parser.parse()
        data.append(parser.benchmarks)

    assignment = [list((x[0], x[1]) for x in z) for z in config['assignment']]
    assignment = list(assignment)
    options = {}
    for outer in config['assignment']:
        for item in outer:
            if len(item) > 2:
                # We have custom draw options
                options[item[1]] = item[2]

    lineplot = False
    if "style" in config and config["style"] == "line":
        lineplot = True
    logplot = False
    if "scale" in config and config["scale"] == "log":
        logplot = True
    zero = False
    if "yfix" in config and config["yfix"] == "zero":
        zero = True

    plotter = Plotter(data, assignment, config['axis'], lineplot, options, logplot, zero)
    if "mode" in config and config["mode"] == "history":
        plotter.groupDataByFile()
    else:
        plotter.groupData()
    if "preprocess" in config and config["preprocess"] == "speedup":
        plotter.groupToSpeedup()
    if "preprocess" in config and config["preprocess"] == "diff":
        plotter.groupToDiff()
    if "preprocess" in config and config["preprocess"] == "diffSpeedup":
        plotter.groupToDiffSpeedup()

    size = [5, 8]
    if "size" in config and len(size) == 2:
        size = config["size"]

    plotter.plot(config['name'], config['filename'], size)
