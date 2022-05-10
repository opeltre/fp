#!/usr/bin/env python
import os
from setuptools import setup

with open('./requirements.txt', 'r') as f:
    requirements = f.read().strip().split('\n')

setup(
    name    ='fp',
    version ='0.1',
    description ="Functional and polymorphic library",
    author      ="Olivier Peltre",
    author_email='opeltre@gmail.com',
    url     ='https://github.com/opeltre/fp',
    license ='MIT',
    install_requires=requirements,
    packages = ['fp']
)
