#!/usr/bin/env python3

from setuptools import setup

setup(name='dataviz',
      version='0.1',
      description='Data visualization script',
      author='Maximilian Falkenstein',
      author_email='maxf@njsm.de',
      packages=['dataviz'],
      install_requires=['pandas', 'matplotlib', 'Jinja2', 'python-gitlab'],
      scripts=['bin/plot_file.py', 'bin/fetch_data.py', 'bin/plot_gcd_histogram.py']
      )

# mpld3 is required from "git+https://github.com/javadba/mpld3@display_fix", you'll need to git install manually
