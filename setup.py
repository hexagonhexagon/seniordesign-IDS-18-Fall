#!/usr/bin/env python

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='two-stage-ids',
    version='0.1',
    description='Two Stage Intrusion Detection for CAN bus',
    long_description=long_description,
    author='UM-Dearborn CIS Team 10 W19',

    # python_requires='>=3.6, <3.7',
    python_requires='>=3.6',
    install_requires=['numpy', 'tensorflow', 'PyQt5'],
    extras_require={
        'test': ['pytest']
    },

    packages=find_packages('src'),
    package_dir={'': 'src'}
)
