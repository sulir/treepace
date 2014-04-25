"""A tree-searching virtual machine and searching branch implementation."""

from treepace.relations import Descendant
import treepace.subtree
from treepace.utils import ReprMixin

class SearchMachine(ReprMixin):
    """A tree-searching virtual machine."""
    
    def __init__(self, node, instructions, variables):
        """Initialize the VM with the default state."""
        self.branches = [SearchBranch(node, instructions[:], self)]
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
    
    def __init__(self, node, instructions, vm):
        """Each branch is represented by a set of current group numbers,
        a match object (a subtree list containing current results), a context
        node, a current relation and an instruction list."""
        self.groups = {0}
        self.match = treepace.subtree.Match([treepace.subtree.Subtree()])
        self.node = node
        self.relation = Descendant
        self.instructions = instructions
        self.vm = vm
    
    def copy(self):
        """Return a copy of this branch which can be modified without affecting
        the original branch."""
        branch = SearchBranch(self.node, self.instructions[:], self.vm)
        branch.groups = self.groups.copy()
        branch.match = self.match.copy()
        branch.relation = self.relation
        return branch
    
    def __str__(self):
        """Return the branch information as a string."""
        fmt = "groups: %s, match: %s, node: %s, relation: %s, instructions: %s"
        return fmt % (self.groups, list(map(str, self.match.groups())),
            self.node, self.relation.name, list(map(str, self.instructions)))
