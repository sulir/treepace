import unittest
from treepace.formats import *

class TestFormats(unittest.TestCase):
    INDENTED = '''root
                      item1
                          sub
                              subsub
                      item2
                      item3'''
    PARENTHESIZED = 'root (item1 (sub (subsub)) item2 item3)'
    XML = '''<root>
                 <item1>
                     <sub>
                         <subsub />
                     </sub>
                 </item1>
                 <item2 />
                 <item3 />
             </root>'''
    TREE = Node('root', [Node('item1', [Node('sub', [Node('subsub')])]),
                         Node('item2'),
                         Node('item3')])
    
    def test_load_indented(self):
        self.assertEquals(load_indented(self.INDENTED), self.TREE)
        with self.assertRaises(MultipleRootsError):
            load_indented('root1\nroot2')
    
    def test_save_indented(self):
        self.assertEquals(save_indented(self.TREE), self.INDENTED)
    
    def test_load_par(self):
        self.assertEquals(load_par(self.PARENTHESIZED), self.TREE)
    
    def test_save_par(self):
        self.assertEquals(save_par(self.TREE), self.PARENTHESIZED)
    
    def test_load_xml(self):
        self.assertEquals(load_xml(self.XML), self.TREE)
    
    def test_save_xml(self):
        self.assertEquals(save_xml(self.TREE), self.XML)
