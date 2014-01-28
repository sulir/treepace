import unittest
from treepace.formats import *
from textwrap import dedent

class TestFormats(unittest.TestCase):
    INDENTED = '''\
                root
                    item1
                        sub
                            subsub
                    item2
                    item3'''
    PARENTHESIZED = 'root (item1 (sub (subsub)) item2 item3)'
    XML = '''\
            <root>
                <item1>
                    <sub>
                        <subsub/>
                    </sub>
                </item1>
                <item2/>
                <item3/>
            </root>'''
    TREE = Node('root', [Node('item1', [Node('sub', [Node('subsub')])]),
                         Node('item2'),
                         Node('item3')])
    
    def test_load_indented(self):
        self.assertEqual(load_indented(self.INDENTED), self.TREE)
        with self.assertRaises(InvalidFormatError):
            load_indented('root1\nroot2')
    
    def test_save_indented(self):
        result = save_indented(self.TREE).splitlines()
        expected = dedent(self.INDENTED).splitlines()
        self.assertEqual(result, expected)
    
    def test_load_par(self):
        self.assertEqual(load_par(self.PARENTHESIZED), self.TREE)
        self.assertRaises(InvalidFormatError, lambda: load_par('a(('))
        self.assertRaises(InvalidFormatError, lambda: load_par('a b'))
    
    def test_save_par(self):
        self.assertEqual(save_par(self.TREE), self.PARENTHESIZED)
    
    def test_load_xml(self):
        self.assertEqual(load_xml(self.XML), self.TREE)
    
    def test_save_xml(self):
        result = save_xml(self.TREE).splitlines()
        expected = dedent(self.XML).splitlines()
        self.assertEqual(result, expected)
