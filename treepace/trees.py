from itertools import chain
from treepace.formats import ParenText
from treepace.nodes import Node

class Tree:
    """A general tree which can contain any types of nodes."""
    
    def __init__(self, root):
        """Initialize the tree with a root node which can never be deleted
        (only replaced)."""
        self._root = root
    
    @property
    def root(self):
        """Return the root node."""
        return self._root
    
    @root.setter
    def root(self, _root):
        """Set a new root node-"""
        self._root = _root
    
    @classmethod
    def load(cls, string, fmt=ParenText, node_class=Node):
        """Create a new tree by importing it from a string in a given format."""
        input_format = fmt() if callable(fmt) else fmt
        return cls(input_format.load_tree(string, node_class))
    
    def save(self, fmt):
        """Export the tree to a string in a given format."""
        return (fmt() if callable(fmt) else fmt).save_tree(self.root)
    
    def preorder(self):
        """Return a generator for pre-order tree traversal."""
        yield self.root
        for child in self.root.children:
            for item in Tree(child).preorder():
                yield item
    
    def node(self, value):
        """Return the first node with the given value (using string
        comparison)."""
        compare = lambda node: str(node.value) == str(value)
        return next(filter(compare, self.preorder()), None)
    
    def search(self, pattern, start=None):
        """Search the whole tree for a given subtree."""
        def traverse(node, result):
            if node.match(pattern):
                result.append(node)
            for child in node.children:
                traverse(child, result)
            return result
        
        return traverse(start or self.root, [])
    
    def match(self, pattern):
        """Return True if the pattern captures the whole tree from the root
        to the leaves."""
        pass
    
    def replace(self, pattern, replacement):
        """Replace each found subtree with a new subtree.
        
        The replacement can be a tree object, a string containing
        back-references or a callback function returning the new tree.
        """
        if callable(replacement):
            pass
        else:
            pass
    
    def transform(self, program):
        """Execute the transformation program which can contain multiple rules
        in the form: pattern -> replacement."""
        pass
    
    def __repr__(self):
        """Return a parenthesized-text representation of this tree."""
        return self.save(ParenText)
    
    def __eq__(self, other):
        """Values of all tree nodes are compared."""
        self_subtrees = [Tree(c) for c in self.root.children]
        other_subtrees = [Tree(c) for c in other.root.children]
        return (self.root.value == other.root.value
                and self_subtrees == other_subtrees)


class Subtree:
    """A connected part of a tree with one root node and one or more leaves.
    
    The main tree should not be changed while its subtree is in use.
    """
    
    def __init__(self, nodes):
        """Initialize the subtree with a nonempty list of nodes."""
        self._root = nodes[0]
        self._nodes = {self._root}
        for node in nodes[1:]:
            self.add_node(node)
    
    def add_node(self, node):
        """Add the node to the subtree.
        
        It must be connected to some node currently present in the subtree.
        """
        if node == self._root.parent:
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
        
        return Tree(make_tree(self._root))
    
    def __repr__(self):
        """Return a text representation of the subtree (as if it was a tree)."""
        return str(self.to_tree())
    
    def __eq__(self, other):
        """Two subtrees are equal if they contain the same set of nodes."""
        return self._nodes == other._nodes
