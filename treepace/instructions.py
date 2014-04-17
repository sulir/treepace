"""Tree-searching and replacing virtual machine instructions."""

from treepace.machine import SearchBranch
from treepace.mixins import EqualityMixin, ReprMixin
import treepace.trees

class Instruction(EqualityMixin, ReprMixin):
    """A base class for all instructions."""
    
    pass


class Find(Instruction):
    """An instruction searching for nodes which are in the currently set
    relationship with the context node and match the predicate."""
    
    def __init__(self, expression):
        self.expression = expression
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
    
    def __str__(self):
        return "FIND %s" % self.expression


class SetRelation(Instruction):
    """An instruction which sets the relation to be used for next search."""
    
    def __init__(self, relation):
        self.relation = relation
    
    def execute(self):
        self.vm._relation = self.relation
    
    def __str__(self):
        return "REL %s" % self.relation.name


class GroupStart(Instruction):
    """An instruction used to mark a numbered group start."""
    
    def __init__(self, number):
        self.number = number
    
    def execute(self):
        self.vm._groups.add(self.number)
        for branch in self.vm._branches:
            branch.match.groups().append(treepace.trees.Subtree())
    
    def __str__(self):
        return "GRPS %d" % self.number


class GroupEnd(Instruction):
    """An instruction marking a numbered group end."""
    
    def __init__(self, number):
        self.number = number
    
    def execute(self):
        self.vm._groups.remove(self.number)
    
    def __str__(self):
        return "GRPE %d" % self.number

class Reference(Instruction):
    """A back-reference to a numbered group."""
    
    def __init__(self, number):
        self.number = number
    
    def execute(self):
        pass
    
    def __str__(self):
        return "REF %d" % self.number