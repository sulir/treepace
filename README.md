Treepace - Tree Transformation Language
=======================================

[![Build Status](https://travis-ci.org/sulir/treepace.png?branch=master)](https://travis-ci.org/sulir/treepace)

*Treepace* (**tree** **pa**ttern repla<b>ce</b>) is a Python library offering a concise, embeddable language for searching and replacing parts of tree structures.

The main goals are:

* simple API and "one line per transformation" syntax - e.g. `tree.transform('list/item -> ul/li')`
* bidirectional integration with the host language - transformations can call Python functions easily
* nodes can receive notifications about each change which is useful for visualization, debugging and mapping to resources like file system
