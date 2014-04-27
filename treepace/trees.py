"""The main tree class and a subtree implementation."""

from itertools import chain
from treepace.build import BuildMachine
from treepace.compiler import Compiler
from treepace.formats import ParenText
from treepace.nodes import Node
from treepace.replace import ReplaceError, ReplaceStrategy
from treepace.search import SearchMachine
from treepace.utils import EqualityMixin, ReprMixin

class TreeBase(EqualityMixin, ReprMixin):
    """An abstract class containing the interface and implementation common
    for both a tree and a subtree."""
    
    @property
    def root(self):
        """Return the current root node."""
        return self._root
    
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
            children = self._node_children(context)
            if children:
                for item in down():
                    yield item
                for index, child in enumerate(children):
                    if index != 0:
                        for item in right():
                            yield item
                    for item in generate(child):
                        yield item
                for item in up():
                    yield item
        
        return generate(self._root)
    
    def preorder(self):
        """Return a generator for pre-order tree traversal."""
        return self.traverse(lambda node: [node])
    
    def node(self, value):
        """Return the first node with the given value (using string
        comparison)."""
        compare = lambda node: str(node.value) == str(value)
        return next(filter(compare, self.preorder()), None)
    
    def leaves(self):
        """Return all leaves of the subtree."""
        def find_leaves(node):
            children = list(self._node_children(node))
            return chain(*map(find_leaves, children)) if children else [node]
        
        return list(find_leaves(self._root))


class Tree(TreeBase):
    """A general tree which can contain any types of nodes."""
    
    def __init__(self, root):
        """Initialize the tree with a root node which can never be deleted
        (only replaced)."""
        self._root = root
    
    @TreeBase.root.setter
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
        if not callable(replacement):
            instructions = Compiler.compile_replacement(replacement)
        
        for match in matches:
            if callable(replacement):
                tree = replacement(match)
            else:
                tree = BuildMachine(match, instructions, variables).build()
            match.group().replace_by(tree)
    
    def transform(self, program, **variables):
        """Execute the transformation program which can contain multiple rules
        in the form: pattern -> replacement."""
        pass
    
    def copy(self):
        """Shallow-copy the tree."""
        def make_tree(node):
            return Node(node.value, (make_tree(c) for c in node.children))
        
        return Tree(make_tree(self._root))
    
    def _node_children(self, node):
        return node.children
    
    def __str__(self):
        """Return a parenthesized-text representation of this tree."""
        return self.save(ParenText)
    
    def __eq__(self, other):
        """Values of all tree nodes are compared."""
        self_subtrees = [Tree(c) for c in self.root.children]
        other_subtrees = [Tree(c) for c in other.root.children]
        return (self.root.value == other.root.value
                and self_subtrees == other_subtrees)


class Subtree(TreeBase):
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
    
    def connected_leaves(self):
        """Return leaves of the subtree which have children in the main tree."""
        return [leaf for leaf in self.leaves() if leaf.children]
    
    def to_tree(self):
        """Shallow-copy node values into a new tree (with new nodes)."""
        def make_tree(node):
            children = (make_tree(child) for child in self._node_children(node))
            return Node(node.value, children)
        
        return Tree(make_tree(self._root)) if self._root else None
    
    def replace_by(self, tree):
        """Try available replacement strategies and raise an exception if
        neither of them is applicable."""
        for strategy in ReplaceStrategy.all_strategies():
            replacer = strategy(self, tree)
            if replacer.test():
                replacer.apply()
                return
        raise ReplaceError("Ambiguous replacement")
    
    def copy(self):
        """Return a shallow copy of the subtree (a new node set is created,
        but the node references point to the same nodes)."""
        subtree = Subtree([self._root])
        subtree._nodes = self._nodes.copy()
        return subtree
    
    def _node_children(self, node):
        return filter(lambda child: child in self._nodes, node.children)
    
    def __str__(self):
        """Return a text representation of the subtree (as if it was a tree)."""
        return str(self.to_tree())
