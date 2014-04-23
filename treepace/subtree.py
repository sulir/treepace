"""A subtree and a searching match."""

from itertools import chain
from treepace.nodes import Node
import treepace.tree
from treepace.utils import EqualityMixin, ReprMixin

class Subtree(EqualityMixin, ReprMixin):
    """A connected part of a tree with one root node and one or more leaves.
    
    The main tree should not be changed while its subtree is in use.
    """
    
    def __init__(self, nodes=[]):
        """Initialize the subtree with a (possibly empty) list of nodes."""
        self._root = None
        self._nodes = set()
        for node in nodes:
            self.add_node(node)
    
    def add_node(self, node):
        """Add the node to the subtree.
        
        It must be connected to some node currently present in the subtree.
        """
        if self._root is None or node == self._root.parent:
            self._root = node
        elif node.parent not in self._nodes:
            raise ValueError("Disconnected subtree node")
        self._nodes.add(node)
    
    @property
    def root(self):
        """Return the current root node of the subtree."""
        return self._root
    
    def leaves(self):
        """Return all leaves of the subtree."""
        def find_leaves(root):
            children = [x for x in root.children if x in self._nodes]
            return chain(*map(find_leaves, children)) if children else [root]
        
        return list(find_leaves(self._root))
    
    def connected_leaves(self):
        """Return leaves of the subtree which have children in the main tree."""
        return [leaf for leaf in self.leaves() if leaf.children]
    
    def to_tree(self):
        """Shallow-copy nodes of the subtree into a new tree."""
        def make_tree(subtree_node):
            tree_node = Node(subtree_node.value)
            for child in [x for x in subtree_node.children if x in self._nodes]:
                tree_node.add_child(make_tree(child))
            return tree_node
        
        return treepace.tree.Tree(make_tree(self._root)) if self._root else None
    
    def copy(self):
        """Return a shallow copy of the subtree (a new node set is created,
        but the node references point to the same nodes)."""
        subtree = Subtree([self._root])
        subtree._nodes = self._nodes.copy()
        return subtree
    
    def __str__(self):
        """Return a text representation of the subtree (as if it was a tree)."""
        return str(self.to_tree())


class Match(ReprMixin):
    """A match is a list of groups; each group is one subtree."""
    
    def __init__(self, groups):
        """Initialize a match with a list of subtrees."""
        self._subtrees = groups
    
    def group(self, number=0):
        """Return the given group; group 0 is the whole match."""
        return self._subtrees[number]
    
    def groups(self):
        """Return the list of all groups."""
        return self._subtrees
    
    def copy(self):
        """Return a list of copies of all subtrees."""
        return Match(list(map(lambda x: x.copy(), self._subtrees)))
    
    def __str__(self):
        """Return a string containing all groups (subtrees)."""
        return str(list(map(str, self._subtrees)))
