"""Tree replacing strategies."""

from itertools import zip_longest

class ReplaceStrategy:
    """A tree replacing strategy is an algorithm for replacement of a subtree
    with an another tree which is applicable only if some condition is met."""
    
    def __init__(self, old, new):
        """Set an old subtree and a new tree."""
        self._old = old
        self._new = new
    
    @staticmethod
    def all_strategies():
        """Return a list of all strategies in the order they should be tried."""
        return [SameShape, ToOneNode]


class SameShape(ReplaceStrategy):
    """Replacement of a subtree by a tree with the same shape."""
    
    def test(self):
        """Traverse and compare the trees, ignoring the values."""
        generate = {k:(lambda *_: [k]) for k in ('node', 'down', 'right', 'up')}
        subtree = self._old.to_tree().traverse(**generate)
        replacement = self._new.traverse(**generate)
        return all(x == y for x, y in zip_longest(subtree, replacement))
    
    def apply(self):
        """Set the subtree node values to the values of the tree."""
        for old, new in zip(self._old.preorder(), self._new.preorder()):
            old.value = new.value


class ToOneNode(ReplaceStrategy):
    """Replacement of a subtree by one node."""
    
    def test(self):
        """The new tree must consist of only one node."""
        return not self._new.root.children
    
    def apply(self):
        """The replacement node child list will consist of all children
        of the original subtree leaves."""
        while len(self._old.nodes) > 1:
            for leaf in list(self._old.leaves()):
                self._old.remove_node(leaf)
                index = leaf.index
                for child in reversed(leaf.children):
                    leaf.parent.insert_child(child, index)
                leaf.delete()
        self._old.root.value = self._new.root.value


class ReplaceError(Exception):
    """Raised when the replacement cannot be accomplished."""
    pass
