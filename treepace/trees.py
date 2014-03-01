"""Tree interfaces and implementations."""

import sys

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
        child._parent = self
        self._children.append(child)
    
    def insert_child(self, child, index):
        """Insert a child node at the specified index."""
        child._parent = self
        self._children.insert(index, child)
    
    def delete_child(self, index):
        """Delete the child node at the specified *index*."""
        self._children[index]._parent = None
        del self._children[index]
    
    def path(self):
        result = []
        node = self
        while node:
            result.insert(0, str(node.value))
            node = node.parent
        return "/".join(result)
    
    def __repr__(self):
        """Return a string representation of this node and all children
        (recursively)."""
        return str(self.value) + str(self._children)
    
    def __eq__(self, other):
        """The node values themselves and then the children values are
        compared (recursively)."""
        return self._value == other._value and self._children == other._children


class LogNode(Node):
    """A tree node which writes human-readable information about all changes
    to a file (or standard output)."""
    
    def __init__(self, value, children=[], file=sys.stdout):
        self._file = file
        super().__init__(value, children)
    
    @Node.value.setter
    def value(self, _value):
        old_path = self.path()
        Node.value.fset(self, _value)
        self._log("Change value of '%s' to '%s'", old_path, str(_value))
    
    def add_child(self, child):
        super().add_child(child)
        self._log("Add child '%s' to '%s'", str(child.value), self.path())
    
    def insert_child(self, child, index):
        super().insert_child(child, index)
        info = str(child.value), index, self.path()
        self._log("Insert child '%s' at index %d of '%s'", *info)
    
    def delete_child(self, index):
        path = self.children[index].path()
        super().delete_child(index)
        self._log("Delete node '%s'", path)
    
    def _log(self, text, *args):
        print(text % args, file=self._file)
