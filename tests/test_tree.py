import unittest
from treepace.tree import Tree

class TestTree(unittest.TestCase):
    def test_search(self):
        source = Tree.load('a (b (c) b (c) d a)')
        expected = Tree.load('a (b (c) d a)')
        for match in source.search('{a} < b <c> & d, $1'):
            self.assertEqual(match.group().to_tree(), expected)
            self.assertEqual(match.group(1).to_tree(), Tree.load('a'))
    
    def test_replace(self):
        pass
