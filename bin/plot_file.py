#!/usr/bin/env python3

from dataviz import Parser, Plotter

defaults = {
    'sparsity': '0',
    'columns': '16',
    'type': 'int16',
}

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

assignment = [
    [
        ('BM_ISL_Rowops_AVX512_checked_.*', 'AVX512 checked'),
        ('BM_ISL_Rowops_AVX512_unchecked_.*', 'AVX512 unchecked')
    ]
]

parser = Parser("perf-isl.json", defaults)
parser.parse()
plotter = Plotter([parser.benchmarks], assignment, axis)
plotter.groupData()
plotter.plot("AVX512 rowops performance (no sparsity)", "checked_rowops")
