#!/usr/bin/env python

"""Package setup script; requires setuptools (or Python >=3.4 which
bundles it)."""

from setuptools import setup

setup(name='Treepace',
      version='1.0.preview',
      description='Tree Transformation Language',
      author='Matúš Sulír',
      url='https://github.com/sulir/treepace',
      packages=['treepace'],
      test_suite='tests',
      install_requires='parsimonious==0.5',
     )
