"""Support for importing trees from various formats (tabulated text, XML, ...)
and exporting them.

In contrast to resource-mapping, importing/exporting loads and saves trees to
their external representation on demand, not after every change.
"""

from treepace.trees import Node

def load_indented(string):
    """Create a tree from the tab- or space-indented string."""
    return Node(None)

def save_indented(tree, indent='    '):
    """Create a space- or tab-indented string from the tree."""
    return ''

def load_par(string):
    """Create a tree from the parenthesized string."""
    return Node(None)

def save_par(tree):
    """Create a parenthesized string from the tree."""
    return ''

def load_xml(string):
    """Create a tree from the XML string."""
    return Node(None)

def save_xml(tree):
    """Create an XML string from the tree."""
    return ''

class MultipleRootsError(Exception):
    pass