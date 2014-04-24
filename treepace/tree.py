"""The main tree class implementation."""

from treepace.compiler import Compiler
from treepace.formats import ParenText
from treepace.nodes import Node
from treepace.search import SearchMachine
from treepace.utils import EqualityMixin, ReprMixin

class Tree(EqualityMixin, ReprMixin):
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
        """Set a new root node."""
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
        return self.traverse(lambda node: [node])
    
    def node(self, value):
        """Return the first node with the given value (using string
        comparison)."""
        compare = lambda node: str(node.value) == str(value)
        return next(filter(compare, self.preorder()), None)
    
    def search(self, pattern, **variables):
        """Search the whole tree for a given subtree."""
        instructions = Compiler.compile_pattern(pattern)
        return SearchMachine(self.root, instructions, variables).search()
    
    def match(self, pattern):
        """Return True if the pattern captures the whole tree from the root
        to the leaves."""
        pass
    
    def replace(self, pattern, replacement, **variables):
        """Replace each found subtree with a new subtree.
        
        The replacement can be a string containing back-references or
        a callback function returning the new tree.
        """
        matches = self.search(pattern, **variables)
        
        if callable(replacement):
            for match in matches:
                tree = replacement(match)
        else:
            pass
    
    def transform(self, program, **variables):
        """Execute the transformation program which can contain multiple rules
        in the form: pattern -> replacement."""
        pass
    
    def traverse(self, node=lambda node: [], down=lambda: [], right=lambda: [],
                 up=lambda: []):
        """Traverse the tree in a pre-order manner with direction signaling.
        
        For each visited node or direction, execute the supplied function and
        generate the items which it returned. For example, given the tree
        'a (b c)', the resulting sequence is node(a), down(), node(b), right(),
        node(c), up().
        """
        def generate(context):
            for item in node(context):
                yield item
            if context.children:
                for item in down():
                    yield item
                for index, child in enumerate(context.children):
                    if index != 0:
                        for item in right():
                            yield item
                    for item in generate(child):
                        yield item
                for item in up():
                    yield item
        
        return generate(self._root)
    
    def copy(self):
        """Shallow-copy the tree."""
        def make_tree(node):
            return Node(node.value, [make_tree(c) for c in node.children])
        
        return Tree(make_tree(self._root))
    
    def __str__(self):
        """Return a parenthesized-text representation of this tree."""
        return self.save(ParenText)
    
    def __eq__(self, other):
        """Values of all tree nodes are compared."""
        self_subtrees = [Tree(c) for c in self.root.children]
        other_subtrees = [Tree(c) for c in other.root.children]
        return (self.root.value == other.root.value
                and self_subtrees == other_subtrees)
