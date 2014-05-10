"""Support for importing trees from various formats (tabulated text, XML, ...)
and exporting them.

In contrast to resource-mapping, importing/exporting loads and saves trees to
their external representation on demand, not after every change.
"""

import json
import math
import re
import textwrap
import treepace.trees
from xml.dom import minidom
from xml.etree import ElementTree

class IndentedText:
    """A text where the indentation level determines the node level."""
    
    def load_tree(self, string, node_class):
        """Create a tree from the tab- or space-indented string.
        
        The indentation type is automatically recognized.
        """
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
                stack[level:] = [node_class(value)]
            else:
                raise InvalidFormatError("Level too large")
            if level > 0:
                stack[-2].add_child(stack[-1])
        return stack[0]
    
    def save_tree(self, tree, indent='    '):
        """Create a space- or tab-indented string from the tree."""
        def indented(node, level):
            result = level * indent + str(node) + '\n'
            for child in node.children:
                result += indented(child, level + 1)
            return result
        
        return indented(tree, 0)


class ParenText:
    """A text starting with a root node, followed by children enclosed
    in parentheses and siblings divided by spaces."""
    
    def load_tree(self, string, node_class):
        """Create a tree from the parenthesized string."""
        tokens = re.findall(r'\(|\)|[^\(\)\s]+', string)
        root = node_class(tokens.pop(0))
        
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
                    node.add_child(node_class(token))
        
        if tokens and tokens.pop(0) != '(':
            raise InvalidFormatError("Multiple root nodes")
        parse(root)
        return root
    
    def save_tree(self, tree):
        """Create a parenthesized string from the tree."""
        result = str(tree)
        if tree.children:
            for i, child in enumerate(tree.children):
                result += (' (' if i == 0 else ' ') + self.save_tree(child)
            result += ')'
        
        return result


class XmlText:
    """A string containing an XML document."""
    
    def load_tree(self, string, node_class):
        """Create a tree from the XML string."""
        doc = ElementTree.fromstring(string)
        node = node_class(doc.tag)
        
        def load(doc, node):
            for elem in doc:
                new_node = node_class(elem.tag)
                node.add_child(new_node)
                for attr in elem.attrib:
                    new_node.add_child(node_class({attr: elem.attrib[attr]}))
                if elem.text and not elem.text.isspace():
                    new_node.add_child(node_class({'xmltext': elem.text}))
                load(elem, new_node)
                if elem.tail and not elem.tail.isspace():
                    tail = node_class({'xmltext': elem.tail})
                    new_node.parent.add_child(tail)
        
        load(doc, node)
        return node
    
    def save_tree(self, tree):
        """Create an XML string from the tree."""
        doc = ElementTree.Element(str(tree))
        
        def save(node, doc):
            sub = None
            for child in node.children:
                if isinstance(child.value, dict):
                    for key, value in child.value.items():
                        if key == 'xmltext':
                            if sub is None:
                                doc.text = value
                            else:
                                sub.tail = value
                        else:
                            doc.attrib[key] = value
                else:
                    sub = ElementTree.SubElement(doc, str(child))
                    save(child, sub)
        
        save(tree, doc)
        xml_str = ElementTree.tostring(doc, encoding='unicode')
        return minidom.parseString(xml_str).documentElement.toprettyxml('    ')


class DotText:
    """A string in DOT graph description language, used by Graphviz."""
    
    TEMPLATE = re.sub(r'\s+', '', '''digraph {
    graph [ranksep=0.2];
    node [shape=box, width=0.05, height=0.05, margin=0.04, color="#C7C7C7", 
          style=filled, fillcolor="#F3F3F3", fontsize=10, fontcolor="#333333"];
    edge [penwidth=1, arrowhead=none, color="#C7C7C7"];%s}''')
    NODE_TPL = 'n%d[label=%s%s];'
    EDGE_TPL = 'n%d->n%d%s;'
    
    def save_tree(self, tree, highlight=set()):
        """Generate the DOT language source text containing nodes and edges."""
        result= ""
        nodes = {}
        
        for index, node in enumerate(treepace.trees.Tree(tree).preorder()):
            nodes[node] = index
            color = ''
            if node in highlight:
                color = ',color="#3567A7",fillcolor="#B9D8FF"'
            result += self.NODE_TPL % (index, json.dumps(str(node)), color)
        
        for node, index in nodes.items():
            if node.parent:
                color = ''
                if node.parent in highlight and node in highlight:
                    color = '[color="#3567A7"]'
                result += self.EDGE_TPL % (nodes[node.parent], index, color)
        
        return self.TEMPLATE % result


class InvalidFormatError(Exception):
    """Raised when the imported string is invalid."""
    pass
