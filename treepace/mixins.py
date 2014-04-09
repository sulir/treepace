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