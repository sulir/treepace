from re import sub
import unittest
from treepace.trees import Subtree, Tree

class TestTree(unittest.TestCase):
    def test_search(self):
        source = Tree.load('a (b (c) b (c) d a)')
        expected = Tree.load('a (b (c) d a)')
        for match in source.search('{a} < b <c> & d, $1'):
            self.assertEqual(match.group().to_tree(), expected)
            self.assertEqual(match.group(1).to_tree(), Tree.load('a'))
    
    def test_replace(self):
        tree = Tree.load('a (b (c) b (c))')
        tree.replace('{b} < {c}', '[f($2)] < $1', f=lambda x: sub('c', 'R', x))
        self.assertEqual(tree, Tree.load('a (R (b) R (b))'))


class TestSubtree(unittest.TestCase):
    def test_add_node(self):
        tree = Tree.load('1 (2 (3 (4 (5)) 6))')
        subtree = Subtree([tree.node(2), tree.node(3)])
        subtree.add_node(tree.node(1))
        self.assertEqual(subtree.to_tree(), Tree.load('1 (2 (3))'))
        self.assertRaises(ValueError, lambda: subtree.add_node(tree.node(5)))
        subtree.add_node(tree.node(6))
        self.assertEqual(subtree.to_tree(), Tree.load('1 (2 (3 6))'))
    
    def test_leaves(self):
        tree = Tree.load('root (connected (leaf1) leaf2)')
        subtree = Subtree([tree.node('root'), tree.node('connected'),
            tree.node('leaf2')])
        connected = [tree.node('connected')]
        self.assertEqual(subtree.connected_leaves(), connected)
        self.assertEqual(subtree.leaves(), connected + [tree.node('leaf2')])
