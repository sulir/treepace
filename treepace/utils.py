"""Utility functions and mix-in classes."""

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
    """Default string and debugging representations of objects."""
    
    def __str__(self):
        """Ideally, subclasses should supply their own implementations."""
        return str(self.__dict__)
    
    def __repr__(self):
        """The debug representation is automatically derived from the string
        representation by adding a class name and a unique identifier."""
        identifier = hex(id(self))[2:]
        return "<%s '%s' @%s>" % (self.__class__.__name__, self, identifier)