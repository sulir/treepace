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
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development :: Libraries',
          ]
     )
