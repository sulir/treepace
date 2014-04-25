import unittest
from treepace.subtree import Subtree
from treepace.tree import Tree

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
