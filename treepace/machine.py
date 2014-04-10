"""An abstract machine implementation and its instructions."""

from treepace.mixins import EqualityMixin

class Machine:
    """A tree-searching and transforming virtual machine."""
    pass


class Instruction(EqualityMixin):
    """A base class for all instructions."""
    def __repr__(self):
        return "%s %s" % (self.__class__.__name__, self.__dict__)


class Find(Instruction):
    def __init__(self, predicate):
        self.predicate = predicate


class Relation(Instruction):
    CHILD, SIBLING, NEXT_SIB, PARENT, DESCENDANT = range(5)
    
    def __init__(self, rel_type):
        self.rel_type = rel_type


class GroupStart(Instruction):
    def __init__(self, number):
        self.number = number


class GroupEnd(Instruction):
    def __init__(self, number):
        self.number = number


class Reference(Instruction):
    def __init__(self, number):
        self.number = number