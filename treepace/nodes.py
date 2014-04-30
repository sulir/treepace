"""The basic node implementation, followed by custom node types with specific
behavior."""

import sys
from treepace.utils import ReprMixin

class Node(ReprMixin):
    """An in-memory node node with references to children and a parent.
    
    The constructor, the 'value' property setter and the methods 'insert_child'
    and 'delete' are recommended to be overridden in specialized classes.
    """
    
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
        self.insert_child(child, len(self._children))
    
    def insert_child(self, child, index):
        """Insert a child node at the specified index."""
        child._parent = self
        self._children.insert(index, child)
    
    def detach(self):
        """Delete the node (it must not be a root)."""
        del self.parent._children[self.index]
        self._parent = None
    
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
    
    def replace_by(self, node):
        """Replace the node by an another node (including children)."""
        self.value = node.value
        for child in self.children:
            child.detach()
        for child in node.children:
            self.add_child(child)
    
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
    
    def insert_child(self, child, index):
        super().insert_child(child, index)
        info = str(child.value), index, self.str_path()
        self._log("Insert child '%s' at index %d of '%s'", *info)
    
    def detach(self):
        path = self.str_path()
        super().detach()
        self._log("Detach node '%s'", path)
    
    def __del__(self):
        self._log("Delete node '%s'", self.str_path())
    
    def _log(self, text, *args):
        print(text % args, file=self._file)
