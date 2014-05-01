from re import sub
import unittest
from treepace.nodes import Node
from treepace.trees import Subtree, SubtreeError, Tree

class TestTree(unittest.TestCase):
    def test_search(self):
        source = Tree.load('a (b (c) b (c) d a)')
        expected = Tree.load('a (b (c) d a)')
        for match in source.search('{a} < b <c> & d, $1'):
            self.assertEqual(match.group().to_tree(), expected)
            self.assertEqual(match.group(1).to_tree(), Tree.load('a'))
    
    def test_match(self):
        tree = Tree.load('a (a (b c))')
        match = tree.match('a < a < c')[0].group().to_tree()
        self.assertEqual(match, Tree.load('a (a (c))'))
        self.assertFalse(tree.match('a < b, c'))
    
    def test_fullmatch(self):
        tree = Tree.load('a (b c)')
        self.assertTrue(tree.fullmatch('a < b, c'))
        self.assertFalse(tree.fullmatch('a < b'))
    
    def test_replace(self):
        tree = Tree.load('m (n)')
        tree.replace('"non-matching"', 'x')
        self.assertEqual(tree, Tree.load('m (n)'))
        
        tree = Tree.load('a (b (c) b (c))')
        tree.replace('{b} < {c}', '[f($2)] < $1', f=lambda x: sub('c', 'R', x))
        self.assertEqual(tree, Tree.load('a (R (b) R (b))'))
        
        tree = Tree.load('a (b (c (d)) b (c (e)))')
        tree.replace('b < c', 'x')
        self.assertEqual(tree, Tree.load('a (x (d) x(e))'))
        
        tree = Tree.load('a (b c)')
        tree.replace('b', 'x < y, z')
        self.assertEqual(tree, Tree.load('a (x (y z) c)'))
        
        tree = Tree.load('a (b (c) d (e))')
        tree.replace('a < b, d', 'x < y, z')
        self.assertEqual(tree, Tree.load('x (y (c) z (e))'))
        
        tree = Tree.load('a (b (c) d e (f))')
        tree.replace('a < b, d, e', 'w < x < y, z')
        self.assertEqual(tree, Tree.load('w (x (y (c) z(f)))'))
        
        tree = Tree.load('a (b c)')
        repl = lambda match: Tree(Node('x', [Node(match.group().root.value)]))
        tree.replace('a < b', repl)
        self.assertEqual(tree, Tree.load('x (a c)'))
    
    def test_transform(self):
        tree = Tree.load('add (1 add (add (2 3) 4))')
        tree.transform('''
            [isinstance(_, str) and _.isdigit()] -> [int($0)]
            add < {[is_int(_)]}, {[is_int(_)]} -> [$1 + $2]
            ''', is_int=lambda x: isinstance(x, int)
        )
        self.assertEqual(tree, Tree(Node(10)))
        
        tree = Tree.load('a (b)')
        tree.transform('''
            x -> y
            a -> x''')
        self.assertEqual(tree, Tree.load('y (b)'))


class TestSubtree(unittest.TestCase):
    def test_add_node(self):
        tree = Tree.load('1 (2 (3 (4 (5)) 6))')
        subtree = Subtree([tree.node(2), tree.node(3)])
        subtree.add_node(tree.node(1))
        self.assertEqual(subtree.to_tree(), Tree.load('1 (2 (3))'))
        self.assertRaises(SubtreeError, lambda: subtree.add_node(tree.node(5)))
        subtree.add_node(tree.node(6))
        self.assertEqual(subtree.to_tree(), Tree.load('1 (2 (3 6))'))
    
    def test_leaves(self):
        tree = Tree.load('root (connected (leaf1) leaf2)')
        subtree = Subtree([tree.node('root'), tree.node('connected'),
            tree.node('leaf2')])
        connected = [tree.node('connected')]
        self.assertEqual(subtree.connected_leaves, connected)
        self.assertEqual(subtree.leaves, connected + [tree.node('leaf2')])
