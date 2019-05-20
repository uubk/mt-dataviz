#!/usr/bin/env python3

from dataviz import Parser, Plotter

defaults = {
    'sparsity': 0,
    'columns': 16,
}
parser = Parser("../perf-isl.json", defaults)
parser.parse()

axis = [
    {
        'sparsity': 0,
        'columns': 16,
        'type': 'int16_t',
    },
    {
        'sparsity': 0,
        'columns': 16,
        'type': 'int32_t',
    }
]

assigment = [['BM_ISL_Rowops_scalar_unchecked.*', 'BM_ISL_Rowops_AVX512_unchecked_.*/sparsity:0/columns:16']]

plotter = Plotter([parser.benchmarks], assigment, axis)
plotter.groupData()
plotter.plot()