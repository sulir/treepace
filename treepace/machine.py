"""An abstract machine implementation."""

from treepace.mixins import ReprMixin
from treepace.relations import Descendant
import treepace.trees

class Machine(ReprMixin):
    """A tree-searching and replacing virtual machine."""
    
    def __init__(self, node, instructions, variables):
        """Initialize the VM with the default state."""
        self._groups = {0}
        match = treepace.trees.Match([treepace.trees.Subtree()])
        self._branches = [SearchBranch(match, node)]
        self._relation = Descendant
        self._instructions = instructions
        
        for instruction in instructions:
            instruction.vm = self
        self._variables = variables
    
    def run(self):
        """Execute all instructions."""
        while self._instructions and self._branches:
            instruction = self._instructions.pop(0)
            instruction.execute()
    
    @property
    def found(self):
        """Return the search results."""
        return list(map(lambda branch: branch.match, self._branches))
    
    def __str__(self):
        """Return the machine state in a form of a string."""
        return "groups: %s, branches: %s, relation: %s, instructions: %s" % (
            self._groups, list(map(str, self._branches)), self._relation,
            list(map(str, self._instructions)))


class SearchBranch(ReprMixin):
    """The search process can 'divide' itself into multiple branches."""
    
    def __init__(self, match, context_node):
        """Each branch is represented by a match object (a subtree list
        containing current results) and a context node."""
        self.match = match
        self.context_node = context_node
    
    def __str__(self):
        """Return the branch information as a string."""
        return "match: %s, context: %s" % (self.match, self.context_node)
