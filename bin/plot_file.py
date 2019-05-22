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
    plotter = Plotter(data, assignment, config['axis'])
    if "mode" in config and config["mode"] == "history":
        plotter.groupDataByFile()
    else:
        plotter.groupData()
    if "preprocess" in config and config["preprocess"] == "speedup":
        plotter.groupToSpeedup()
    plotter.plot(config['name'], config['filename'])
