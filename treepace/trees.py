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
        """Compare the whole tree with an another tree."""
        self_subtrees = [Tree(c) for c in self.root.children]
        other_subtrees = [Tree(c) for c in other.root.children]
        return (self.root.value == other.root.value
                and self_subtrees == other_subtrees)
