#!/usr/bin/env python3

from distutils.core import setup

setup(name='dataviz',
      version='0.1',
      description='Data visualization script',
      author='Maximilian Falkenstein',
      author_email='maxf@njsm.de',
      packages=['pandas==0.24.2', 'matplotlib==3.1.0', 'Jinja2==2.10.1', 'python-gitlab==1.8.0'],
      )

# mpld3 is required from "git+https://github.com/javadba/mpld3@display_fix", you'll need to git install manually