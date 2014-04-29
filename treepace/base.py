"""Basic tree interface and behavior."""

from itertools import chain
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
    
    @property
    def leaves(self):
        """Return all leaves of the subtree."""
        def find_leaves(node):
            children = list(self._node_children(node))
            return chain(*map(find_leaves, children)) if children else [node]
        
        return list(find_leaves(self._root))
    
    @property
    def inner(self):
        """Return all non-leaf nodes (including the root)."""
        leaves = set(self.leaves)
        return (node for node in self.preorder() if node not in leaves)
