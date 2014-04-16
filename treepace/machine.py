"""An abstract machine implementation and its instructions."""

from treepace.mixins import EqualityMixin
from treepace.relations import Descendant
import treepace.trees

class Machine:
    """A tree-searching and replacing virtual machine."""
    
    def __init__(self, node, instructions):
        """Initialize the VM with the default state."""
        self._groups = {0}
        match = treepace.trees.Match([treepace.trees.Subtree()])
        self._branches = [SearchBranch(match, node)]
        self._relation = Descendant
        self._instructions = instructions
        
        for instruction in instructions:
            instruction.vm = self
        self.replacement = None
    
    def run(self):
        """Execute all instructions."""
        while self._instructions and self._branches:
            instruction = self._instructions.pop(0)
            instruction.execute()
    
    @property
    def found(self):
        """Return the search results."""
        return list(map(lambda branch: branch.match, self._branches))


class SearchBranch:
    """The search process can 'divide' itself into multiple branches."""
    
    def __init__(self, match, context_node):
        """"Each branch is represented by a match object (a subtree list
        containing current results) and a context node."""
        self.match = match
        self.context_node = context_node
    
    def __repr__(self):
        """Return the debugging representation."""
        return str(self.__dict__)


class Instruction(EqualityMixin):
    """A base class for all instructions."""
    
    pass


class Find(Instruction):
    """An instruction searching for nodes which are in the currently set
    relationship with the context node and match the predicate."""
    
    def __init__(self, expression):
        self.code = compile(expression, '<string>', 'eval')
    
    def execute(self):
        new_branches = []
        for old_branch in self.vm._branches:
            for node in self._matching_nodes(old_branch.context_node):
                new_branch = SearchBranch(old_branch.match.copy(), node)
                for group in self.vm._groups:
                    new_branch.match.group(group).add_node(node)
                new_branches.append(new_branch)
        self.vm._branches = new_branches
    
    def _matching_nodes(self, context_node):
        predicate = lambda x: eval(self.code, {'node': x, '_': x.value})
        return filter(predicate, self.vm._relation().search(context_node))


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
        for branch in self.vm._branches:
            branch.match.groups().append(treepace.trees.Subtree())


class GroupEnd(Instruction):
    """An instruction marking a numbered group end."""
    
    def __init__(self, number):
        self.number = number
    
    def execute(self):
        self.vm._groups.remove(self.number)


class Reference(Instruction):
    """A back-reference to a numbered group."""
    
    def __init__(self, number):
        self.number = number
