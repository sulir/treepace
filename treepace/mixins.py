"""Utility mixins - additional functionalities for classes."""

class EqualityMixin:
    """Equality and inequality operator overloading based on attributes."""
    
    def __eq__(self, other):
        """All instance attributes are compared for equality."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            raise NotImplemented
    
    def __ne__(self, other):
        """Just a negation of the equality result."""
        return not self.__eq__(other)


class ReprMixin:
    """An automatic derivation of __repr__ from __str__."""
    
    def __repr__(self):
        """The debug representation is derived from the string representation
        by adding a class name and a unique identifier."""
        identifier = hex(id(self))[2:]
        return "<%s '%s' @%s>" % (self.__class__.__name__, self, identifier)
    
    def __str__(self):
        """Subclasses should supply their own implementations, this is only
        a fail-safe option to avoid infinite recursion caused by the default
        behavior."""
        return ""
