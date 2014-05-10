"""The main tree class and a subtree implementation."""

from treepace.base import TreeBase
from treepace.build import BuildMachine
from treepace.compiler import Compiler
from treepace.formats import ParenText, DotText
from treepace.nodes import Node
from treepace.relations import Identic
from treepace.replace import ReplaceError, ReplaceStrategy
from treepace.search import Match, SearchMachine
from treepace.utils import GraphvizImage

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
    def load(cls, string, fmt=ParenText, node_class=Node, *args, **kwargs):
        """Create a new tree by importing it from a string in a given format."""
        return cls(fmt().load_tree(string, node_class, *args, **kwargs))
    
    def save(self, fmt, *args, **kwargs):
        """Export the tree to a string in a given format."""
        return fmt().save_tree(self.root, *args, **kwargs)
    
    def search(self, pattern, **variables):
        """Search for a given pattern anywhere in the tree and return a list
        of matches."""
        instructions = Compiler.compile_pattern(pattern)
        return SearchMachine(self.root, instructions, variables).search()
    
    def match(self, pattern, **variables):
        """Search for a given pattern from the root node and return a list
        of matches."""
        instrs = Compiler.compile_pattern(pattern)
        machine = SearchMachine(self.root, instrs, variables, relation=Identic)
        return machine.search()
    
    def fullmatch(self, pattern, **variables):
        """If the tree matches the pattern from the root to the leaves, return
        a list of matches, otherwise return an empty list."""
        matches = self.match(pattern, **variables)
        matched_nodes = set().union(*[match.group().nodes for match in matches])
        all_node_count = sum(1 for _ in self.preorder())
        return matches if len(matched_nodes) == all_node_count else []
    
    def replace(self, pattern, replacement, **variables):
        """Replace each found subtree with a new subtree.
        
        The replacement can be a string containing back-references or
        a callback function returning the new tree.
        """
        matches = self.search(pattern, **variables)
        Match.check_disjoint(matches)
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
        in the form: pattern -> replacement.
        
        Each rule is executed while its pattern matches. In addition, the whole
        rule list is looped until no rule matches.
        """
        lines = (line for line in program.splitlines() if line.strip())
        rules = [Compiler.compile_rule(line) for line in lines]
        
        while True:
            rule_matched = False
            for search, replace in rules:
                matches = True
                while matches:
                    machine = SearchMachine(self.root, search, variables)
                    matches = machine.search()
                    Match.check_disjoint(matches)
                    for match in matches:
                        tree = BuildMachine(match, replace, variables).build()
                        match.group().replace_by(tree)
                    if matches:
                        rule_matched = True
            if not rule_matched:
                break
    
    def copy(self):
        """Shallow-copy the tree."""
        def make_tree(node):
            children = (make_tree(child) for child in node.children)
            return node.__class__(node.value, children)
        
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
    
    def _repr_png_(self):
        return GraphvizImage(self.save(DotText)).png()
    
    def _repr_html_(self):
        return GraphvizImage(self.save(DotText)).html()


class Subtree(TreeBase):
    """A subtree is a connected part of a tree with one root node and one
    or more leaves.
    
    Each subtree node reference points to the same object as the node
    reference in the main tree.
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
        elif node.parent not in self._nodes and node not in self._nodes:
            raise SubtreeError("Disconnected subtree node '%s'" % node)
        self._nodes.add(node)
    
    def remove_node(self, node):
        """Remove the given leaf node from the subtree."""
        if not next(self._node_children(node), False):
            self._nodes.remove(node)
            if node == self._root:
                self._root = None
        else:
            raise SubtreeError("Cannot remove non-leaf subtree node")
    
    @property
    def nodes(self):
        """The returned node set should not be modified."""
        return self._nodes
    
    @property
    def connected_leaves(self):
        """Return leaves of the subtree which have children in the main tree."""
        return [leaf for leaf in self.leaves if leaf.children]
    
    def to_tree(self):
        """Shallow-copy subtree node values into a new tree (with new nodes)."""
        def make_tree(node):
            children = (make_tree(child) for child in self._node_children(node))
            return node.__class__(node.value, children)
        
        return Tree(make_tree(self._root)) if self._root else None
    
    def main_tree(self):
        """Return the main tree associated with this subtree.
        
        A new tree is created, but the nodes are not copied.
        """
        root = self._root
        while root.parent:
            root = root.parent
        return Tree(root)
    
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
    
    def _repr_png_(self):
        return GraphvizImage(self.main_tree().save(DotText, self._nodes)).png()


class SubtreeError(Exception):
    """Raised when a subtree cannot be modified in a given way."""
    pass
