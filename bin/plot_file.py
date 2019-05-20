#!/usr/bin/env python3

from dataviz import Parser, Plotter

defaults = {
    'sparsity': '0',
    'columns': '16',
}
parser = Parser("../perf-isl.json", defaults)
parser.parse()

axis = [
    {
        'sparsity': '0',
        'columns': '16',
        'type': 'int16',
    },
    {
        'sparsity': '0',
        'columns': '16',
        'type': 'int32',
    },
    {
        'sparsity': '0',
        'columns': '2',
        'type': 'int16',
    },
    {
        'sparsity': '0',
        'columns': '2',
        'type': 'int32',
    }
]

assigment = [['BM_ISL_Rowops_AVX512_checked_.*', 'BM_ISL_Rowops_AVX512_unchecked_.*']]

plotter = Plotter([parser.benchmarks], assigment, axis)
plotter.groupData()
plotter.plot()