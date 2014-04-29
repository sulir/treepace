"""Tree replacing strategies."""

from itertools import chain, zip_longest

class ReplaceStrategy:
    """A tree replacing strategy is an algorithm for replacement of a subtree
    with an another tree which is applicable only if some condition is met."""
    
    def __init__(self, old, new):
        """Set an old subtree and a new tree."""
        self._old = old
        self._new = new
    
    def _inner_nonsubtree_child(self):
        inner_children = chain(*(inner.children for inner in self._old.inner))
        return any(child not in self._old.nodes for child in inner_children)
    
    @staticmethod
    def all_strategies():
        """Return a list of all strategies in the order they should be tried."""
        return [SameShape, ToOneNode, NoConnectedLeaves, SameLeafCount,
                SameConnectedCount]


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
            for leaf in list(self._old.leaves):
                self._old.remove_node(leaf)
                index = leaf.index
                for child in reversed(leaf.children):
                    leaf.parent.insert_child(child, index)
                leaf.delete()
        self._old.root.value = self._new.root.value


class NoConnectedLeaves(ReplaceStrategy):
    """Replacement of a subtree which does not have any children outside
    the subtree."""
    
    def test(self):
        """"The subtree must not have 'connected leaves' and its inner nodes
        must not have children outside the subtree."""
        no_connected = not self._old.connected_leaves
        return no_connected and not self._inner_nonsubtree_child()
    
    def apply(self):
        """The subtree root node is replaced by the new tree root node."""
        self._old.root.replace_by(self._new.root)


class LeafCountStrategy(ReplaceStrategy):
    """An abstract class representing replacement of a subtree by a tree whose
    leaf count is the same as the count of the subtree's leaves or
    'connected leaves'."""
    
    def test(self):
        """In addition, non-leaf subtree nodes must not have children outside
        of the subtree."""
        same_leaf_count = len(self._leaves()) == len(self._new.leaves)
        return same_leaf_count and not self._inner_nonsubtree_child()
    
    def apply(self):
        """Children of the subtree leaves become the children of the tree
        leaves, then the roots are replaced."""
        for old_leaf, new_leaf in zip(self._leaves(), self._new.leaves):
            for child in old_leaf.children:
                new_leaf.add_child(child)
        self._old.root.replace_by(self._new.root)


class SameLeafCount(LeafCountStrategy):
    """Replacement of a subtree by a tree with the same leaf count."""
    
    def _leaves(self):
        return self._old.leaves


class SameConnectedCount(LeafCountStrategy):
    """Replacement of a subtree by a tree whose leaf count is the same
    as the count of the subtree's 'connected leaves'."""
    
    def _leaves(self):
        return self._old.connected_leaves


class ReplaceError(Exception):
    """Raised when the replacement cannot be accomplished."""
    pass
