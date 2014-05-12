"""A tree-searching virtual machine, searching branch and match
implementation."""

from treepace.relations import Descendant
import treepace.trees
from treepace.utils import ReprMixin, IPythonDotMixin
from treepace.replace import ReplaceError

class SearchMachine(ReprMixin):
    """A tree-searching virtual machine."""
    
    def __init__(self, node, instructions, variables, relation=Descendant):
        """Initialize the VM with the default state."""
        self.branches = [SearchBranch(node, instructions[:], self, relation)]
        self.machine_vars = variables
    
    def search(self):
        """Execute all instructions and return the search results."""
        while any(branch.instructions for branch in self.branches):
            new_branches = []
            for branch in self.branches:
                if branch.instructions:
                    result = branch.instructions.pop(0).execute(branch)
                    if result is not None:
                        new_branches.extend(result)
                    else:
                        new_branches.append(branch)
                else:
                    new_branches.append(branch)
            self.branches = new_branches
        
        return [branch.match for branch in self.branches]
    
    def __str__(self):
        """Return the machine state in a form of a string."""
        return "branches: %s, vars: %s" % (self.branches, self.machine_vars)


class SearchBranch(ReprMixin):
    """The search process can 'divide' itself into multiple branches."""
    
    def __init__(self, node, instructions, vm, relation):
        """Each branch is represented by a set of current group numbers,
        a match object (a subtree list containing current results), a context
        node, a current relation and an instruction list."""
        self.groups = {0}
        self.match = Match([treepace.trees.Subtree()])
        self.node = node
        self.relation = relation
        self.instructions = instructions
        self.vm = vm
    
    def copy(self):
        """Return a copy of this branch which can be modified without affecting
        the original branch."""
        branch = SearchBranch(self.node, self.instructions[:], self.vm,
                              self.relation)
        branch.groups = self.groups.copy()
        branch.match = self.match.copy()
        return branch
    
    def __str__(self):
        """Return the branch information as a string."""
        fmt = "groups: %s, match: %s, node: %s, relation: %s, instructions: %s"
        return fmt % (self.groups, list(map(str, self.match.groups())),
            self.node, self.relation.name, list(map(str, self.instructions)))


class Match(ReprMixin, IPythonDotMixin):
    """A match is a list of groups; each group is one subtree."""
    
    def __init__(self, groups):
        """Initialize a match with a list of subtrees."""
        self._subtrees = groups
    
    def group(self, number=0):
        """Return the given group; group 0 is the whole match."""
        return self._subtrees[number]
    
    def groups(self):
        """Return the list of all groups."""
        return self._subtrees
    
    def copy(self):
        """Return a list of copies of all subtrees."""
        return Match(list(map(lambda x: x.copy(), self._subtrees)))
    
    @staticmethod
    def check_disjoint(matches):
        """Raise ReplaceError if there exists a node which is present
        in at least two matches from the given list of matches."""
        subtree_nodes = [match.group().nodes for match in matches]
        total_count = sum(map(len, subtree_nodes))
        if len(set().union(*subtree_nodes)) < total_count:
            raise ReplaceError("Overlapping matches")
    
    def __str__(self):
        """Return a string containing all groups (subtrees)."""
        return str(list(map(str, self._subtrees)))
    
    def _repr_dot_(self):
        from treepace.formats import DotText
        return self.group().main_tree().save(DotText, match=self)
