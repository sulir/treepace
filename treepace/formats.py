"""Support for importing trees from various formats (tabulated text, XML, ...)
and exporting them.

In contrast to resource-mapping, importing/exporting loads and saves trees to
their external representation on demand, not after every change.
"""

import math
import re
import textwrap
from xml.dom import minidom
from xml.etree import ElementTree
from treepace.trees import Node

def load_indented(string):
    """Create a tree from the tab- or space-indented string."""
    indent_len = None
    stack = []
    
    for line in filter(str.strip, textwrap.dedent(string).splitlines()):
        value = line.lstrip()
        spaces = len(line) - len(value)
        if spaces and not indent_len:
            indent_len = spaces
        level = math.ceil(spaces / indent_len) if indent_len else 0
        
        if level == 0 and stack:
            raise InvalidFormatError("Multiple root nodes")
        if level <= len(stack):
            stack[level:] = [Node(value)]
        else:
            raise InvalidFormatError("Level too large")
        if level > 0:
            stack[-2].add_child(stack[-1])
    return stack[0]

def save_indented(tree, indent='    '):
    """Create a space- or tab-indented string from the tree."""
    def indented(node, level):
        result = level * indent + node.value + '\n'
        for child in node.children:
            result += indented(child, level + 1)
        return result
    
    return indented(tree, 0)

def load_par(string):
    """Create a tree from the parenthesized string."""
    tokens = re.findall(r'\(|\)|[^\(\)\s]+', string)
    root = Node(tokens.pop(0))
    
    def parse(node):
        while tokens:
            token = tokens.pop(0)
            if token == '(':
                if not node.children:
                    raise InvalidFormatError("Unexpected '('")
                parse(node.children[-1])
            elif token == ')':
                return
            else:
                node.add_child(Node(token))
    
    if tokens and tokens.pop(0) != '(':
        raise InvalidFormatError("Multiple root nodes")
    parse(root)
    return root

def save_par(tree):
    """Create a parenthesized string from the tree."""
    result = tree.value
    if tree.children:
        for i, child in enumerate(tree.children):
            result += (' (' if i == 0 else ' ') + save_par(child)
        result += ')'
    
    return result

def load_xml(string):
    """Create a tree from the XML string."""
    doc = ElementTree.fromstring(string)
    node = Node(doc.tag)
    
    def load(doc, node):
        for child in doc:
            new_node = Node(child.tag)
            node.add_child(new_node)
            load(child, new_node)
    
    load(doc, node)
    return node

def save_xml(tree):
    """Create an XML string from the tree."""
    doc = ElementTree.Element(tree.value)
    
    def save(node, doc):
        for child in node.children:
            sub = ElementTree.SubElement(doc, child.value)
            save(child, sub)
    
    save(tree, doc)
    xml_str = ElementTree.tostring(doc, encoding='unicode')
    return minidom.parseString(xml_str).documentElement.toprettyxml('    ')

class InvalidFormatError(Exception):
    pass
