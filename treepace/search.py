"""A tree-searching virtual machine and its instructions."""

from treepace.relations import Child, Descendant, NextSibling, Parent
import treepace.subtree
from treepace.utils import EqualityMixin, ReprMixin

class SearchMachine(ReprMixin):
    """A tree-searching virtual machine."""
    
    def __init__(self, node, instructions, variables):
        """Initialize the VM with the default state."""
        self.branches = [SearchBranch(node, instructions, self)]
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


class Instruction(EqualityMixin, ReprMixin):
    """Instructions should be immutable."""
    
    pass


class Find(Instruction):
    """An instruction searching for nodes which are in the currently set
    relationship with the context node and match the predicate."""
    
    def __init__(self, expression, **variables):
        """Save the expression in a textual and compiled version."""
        self.expression = expression
        self.code = compile(expression, '<string>', 'eval')
        self.instr_vars = variables
    
    def execute(self, branch):
        """Find the nodes and return a list of branches which should replace
        the supplied branch."""
        new_branches = []
        vm_vars = branch.vm.machine_vars.copy()
        for node in self._matching_nodes(branch.node, branch.relation, vm_vars):
            new_branch = branch.copy()
            for group in new_branch.groups:
                new_branch.match.group(group).add_node(node)
            new_branch.node = node
            new_branches.append(new_branch)
        return new_branches
    
    def _matching_nodes(self, context_node, relation, variables):
        def predicate(node):
            variables.update({'node': node, '_': node.value})
            return eval(self.code, variables)
        
        variables.update(self.instr_vars)
        return filter(predicate, relation().search(context_node))
    
    def __str__(self):
        """Return the string representation of the instruction."""
        return "FIND %s" % self.expression


class SetRelation(Instruction):
    """An instruction which sets the relation to be used for next search."""
    
    def __init__(self, relation):
        """The given relation argument should be a class."""
        self.relation = relation
    
    def execute(self, branch):
        """Set the current relation of the virtual machine."""
        branch.relation = self.relation
    
    def __str__(self):
        """Return the string representation of the instruction."""
        return "REL %s" % self.relation.name


class GroupStart(Instruction):
    """An instruction used to mark a numbered group start."""
    
    def __init__(self, number):
        """Save the group number as an instruction argument."""
        self.number = number
    
    def execute(self, branch):
        """Add the corresponding group number and subtrees to the machine."""
        branch.groups.add(self.number)
        branch.match.groups().append(treepace.subtree.Subtree())
    
    def __str__(self):
        """Return the string representation of the instruction."""
        return "GRPS %d" % self.number


class GroupEnd(Instruction):
    """An instruction marking a numbered group end."""
    
    def __init__(self, number):
        """Save the group number as an instruction argument."""
        self.number = number
    
    def execute(self, branch):
        """Remove the group number from the set of current group numbers."""
        branch.groups.remove(self.number)
    
    def __str__(self):
        """Return the string representation of the instruction."""
        return "GRPE %d" % self.number


class Reference(Instruction):
    """A back-reference to a numbered group."""
    
    def __init__(self, number):
        """Save the group number as an instruction argument."""
        self.number = number
    
    def execute(self, branch):
        """Prepend instructions which will search for a subtree same as
        the given group's subtree."""
        generated = branch.match.group(self.number).to_tree().traverse(
            node  = lambda node: [Find('_ == ref', ref=node.value)],
            down  = lambda: [SetRelation(Child)],
            right = lambda: [SetRelation(NextSibling)],
            up    = lambda: [SetRelation(Parent), Find('True')]
        )
        branch.instructions[:0] = generated
    
    def __str__(self):
        """Return the string representation of the instruction."""
        return "REF %d" % self.number
