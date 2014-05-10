Treepace - Tree Transformation Language
=======================================
[![Build Status](https://travis-ci.org/sulir/treepace.png?branch=master)](https://travis-ci.org/sulir/treepace)

*Treepace* (**tree** <b>pa</b>ttern repla<b>ce</b>) is a Python library offering a concise, embeddable language for searching and replacing parts of tree structures.

The main features are:

* an intuitive API, similar to regex
* "one line per transformation" syntax - e.g. `tree.transform('item -> li')`
* bidirectional integration with the host language - transformations can execute Python code easily
* node values are real objects, not only strings
* thanks to node inheritance, nodes can react to changes which is useful for debugging and mapping to resources like GUI components

Installation
------------
The simplest way is to install the package from PyPI: `pip install treepace`.

Alternatively, clone this repository and run: `python setup.py install`.

Tutorial
--------
The tutorial is available in a form of [IPython Notebook](http://nbviewer.ipython.org/github/sulir/treepace/blob/master/doc/Tutorial.ipynb).