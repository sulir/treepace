"""Tree interfaces and implementations."""

class Node:
    """A general tree node with references to children.
    
    There is no distinction between a whole tree and a node - the tree is just
    represented by a root node.
    """
    
    def __init__(self, value, children=[]):
        """Construct a new tree node."""
        self._value = value
        self._children = children
    
    @property
    def value(self):
        """Return this node's value."""
        return self._value
    
    @value.setter
    def value(self, _value):
        """Set the value of this node -- usually a string, but any object
        is accepted."""
        self._value = _value
    
    @property
    def children(self):
        """Return a tuple containing the child nodes."""
        return tuple(self._children)
    
    def add_child(self, child):
        """Add a child to the end."""
        self._children.append(child)
    
    def delete_child(self, index):
        """Delete the child node at the specified *index*."""
        del self._children[index]
    
    def __repr__(self):
        return str(self.value) + str(self._children)
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
