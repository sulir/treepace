"""An abstract machine implementation and its instructions."""

from treepace.mixins import EqualityMixin
from treepace.relations import Descendant
import treepace.trees

class Machine:
    """A tree-searching and replacing virtual machine."""
    
    def __init__(self, node, instructions):
        """Initialize the VM with the default state."""
        self._groups = {0}
        self._subtrees = [treepace.trees.Subtree()]
        self._node = node
        self._relation = Descendant
        self._instructions = instructions
        
        for instruction in instructions:
            instruction.vm = self
        self.replacement = None
    
    def run(self):
        """Execute all instructions."""
        while self._instructions:
            instruction = self._instructions.pop(0)
            instruction.execute()
    
    @property
    def found(self):
        """Return the search results."""
        return self._subtrees


class Instruction(EqualityMixin):
    """A base class for all instructions."""
    pass


class Find(Instruction):
    """An instruction searching for nodes which are in the currently set
    relationship with the context node and match the predicate."""
    
    def __init__(self, predicate):
        self.predicate = compile(predicate, '<string>', 'eval')
    
    def execute(self):
        for node in self.vm._relation().search(self.vm._node):
            _ = node
            if eval(self.predicate):
                for group in self.vm._groups:
                    self.vm._subtrees[group].add_node(node)
                self.vm._node = node
                break


class SetRelation(Instruction):
    """An instruction which sets the relation to be used for next search."""
    
    def __init__(self, relation):
        self.relation = relation
    
    def execute(self):
        self.vm._relation = self.relation


class GroupStart(Instruction):
    """An instruction used to mark a numbered group start."""
    
    def __init__(self, number):
        self.number = number
    
    def execute(self):
        self.vm._groups.add(self.number)
        self.vm._subtrees.append(treepace.trees.Subtree())


class GroupEnd(Instruction):
    """An instruction marking a numbered group start."""
    
    def __init__(self, number):
        self.number = number
    
    def execute(self):
        self.vm._groups.remove(self.number)


class Reference(Instruction):
    """A back-reference to a numbered group."""
    
    def __init__(self, number):
        self.number = number
