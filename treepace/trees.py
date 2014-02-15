"""Tree interfaces and implementations."""

class Node:
    """A general in-memory tree node with references to children and a parent.
    
    There is no distinction between a whole tree and a node - the tree is just
    represented by a root node.
    """
    
    def __init__(self, value, children=[]):
        """Construct a new tree node.
        
        The optional child node list will be shallow-copied.
        """
        self._value = value
        self._parent = None
        self._children = []
        for child in children:
            self.add_child(child)
    
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
    def parent(self):
        return self._parent
    
    @property
    def children(self):
        """Return a tuple containing the child nodes."""
        return tuple(self._children)
    
    def add_child(self, child):
        """Add a child node to the end."""
        self._children.append(child)
        child._parent = self
    
    def insert_child(self, child, index):
        """Insert a child node at the specified index."""
        self._children.insert(index, child)
        child._parent = self
    
    def delete_child(self, index):
        """Delete the child node at the specified *index*."""
        self._children[index]._parent = None
        del self._children[index]
    
    def __repr__(self):
        """Return a string representation of this node and all children
        (recursively)."""
        return str(self.value) + str(self._children)
    
    def __eq__(self, other):
        """The node values themselves and then the children values are
        compared (recursively)."""
        return self._value == other._value and self._children == other._children

