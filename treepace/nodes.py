"""The basic node implementation, followed by custom node types with specific
behavior."""

import re
import sys
from treepace.utils import ReprMixin

class Node(ReprMixin):
    """An in-memory node node with references to children and a parent."""
    
    def __init__(self, value, children=[]):
        """Initialize a new tree node.
        
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
        """Set the value of this node -- a string, a map or any other object."""
        self._value = _value
    
    @property
    def parent(self):
        """Return the parent node."""
        return self._parent
    
    @property
    def children(self):
        """Return a shallow-copied tuple containing the child nodes."""
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
        """Delete the child node at the specified index."""
        self._children[index]._parent = None
        del self._children[index]
    
    @property
    def index(self):
        """Return a zero-based order of this node among its siblings."""
        siblings = self.parent.children if self.parent else [self]
        return next(i for i, sibling in enumerate(siblings) if sibling == self)
    
    @property
    def level(self):
        """Return this node's vertical level; the root node has a level of 0."""
        return len(self.path()) - 1
    
    def path(self):
        """Return a list of nodes from the root to this node."""
        result = []
        node = self
        while node:
            result.insert(0, str(node.value))
            node = node.parent
        return result
    
    def str_path(self):
        """Return a slash-separated path from the root node to this node."""
        return "/".join(self.path())
    
    def match(self, pattern):
        """Return True if this node matches the pattern (a string literal
        or a Python predicate)."""
        code = re.search(r'\[(.*)\]', pattern)
        if code:
            _ = self.value
            return eval(code.group(1))
        else:
            return str(self.value) == pattern
    
    def __str__(self):
        """Return a string representation of the node's value."""
        return str(self.value)


class LogNode(Node):
    """A tree node which writes human-readable information about all changes
    to a file (or standard output)."""
    
    def __init__(self, value, children=[], file=sys.stdout):
        self._file = file
        super().__init__(value, children)
    
    @Node.value.setter
    def value(self, _value):
        old_path = self.str_path()
        Node.value.fset(self, _value)
        self._log("Change value of '%s' to '%s'", old_path, str(_value))
    
    def add_child(self, child):
        super().add_child(child)
        self._log("Add child '%s' to '%s'", str(child.value), self.str_path())
    
    def insert_child(self, child, index):
        super().insert_child(child, index)
        info = str(child.value), index, self.str_path()
        self._log("Insert child '%s' at index %d of '%s'", *info)
    
    def delete_child(self, index):
        path = self.children[index].str_path()
        super().delete_child(index)
        self._log("Delete node '%s'", path)
    
    def _log(self, text, *args):
        print(text % args, file=self._file)
