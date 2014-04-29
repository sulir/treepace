import re
from textwrap import dedent
import unittest
from treepace.formats import (IndentedText, ParenText, XmlText,
    InvalidFormatError)
from treepace.nodes import Node
from treepace.trees import Tree

class TestFormats(unittest.TestCase):
    INDENTED = '''\
                root
                    item1
                        sub
                            subsub
                    item2
                    item3'''
    PARENTHESIZED = 'root (item1 (sub (subsub)) item2 item3)'
    XML = re.sub(r'\s+', '', '''\
            <root>
                <item1>
                    <sub>
                        <subsub/>
                    </sub>
                </item1>
                <item2/>
                <item3/>
            </root>''')
    TREE = Tree(Node('root', [Node('item1', [Node('sub', [Node('subsub')])]),
                              Node('item2'),
                              Node('item3')]))
    
    def test_load_indented(self):
        self.assertEqual(Tree.load(self.INDENTED, IndentedText), self.TREE)
        with self.assertRaises(InvalidFormatError):
            Tree.load('root1\nroot2', IndentedText)
    
    def test_save_indented(self):
        result = self.TREE.save(IndentedText).splitlines()
        expected = dedent(self.INDENTED).splitlines()
        self.assertEqual(result, expected)
    
    def test_load_par(self):
        fmt = ParenText
        self.assertEqual(Tree.load(self.PARENTHESIZED, fmt), self.TREE)
        self.assertRaises(InvalidFormatError, lambda: Tree.load('a((', fmt))
        self.assertRaises(InvalidFormatError, lambda: Tree.load('a b', fmt))
    
    def test_save_par(self):
        self.assertEqual(self.TREE.save(ParenText), self.PARENTHESIZED)
    
    def test_load_xml(self):
        self.assertEqual(Tree.load(self.XML, XmlText), self.TREE)
    
    def test_save_xml(self):
        self.assertEqual(re.sub(r'\s+', '', self.TREE.save(XmlText)), self.XML)
