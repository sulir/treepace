"""Virtual machine instructions."""

import re
from treepace.relations import Child, NextSibling, Parent
import treepace.trees
from treepace.utils import EqualityMixin, ReprMixin

class Instruction(EqualityMixin, ReprMixin):
    """Instructions should be immutable."""
    
    def _compile_code(self, expression, instr_vars):
        """Compile and save the given Python code."""
        expression = re.sub(r'\$(\d+)', r'group(\1).root.value', expression)
        self.expression = expression.replace('$', 'node.value')
        self.code = compile(self.expression, '<string>', 'eval')
        self.instr_vars = instr_vars
    
    def _evaluate_code(self, machine_vars, match, node=None):
        """Evaluate the saved code in an environment containing auxiliary
        functions, variables from the VM and the instruction object, matched
        groups and (optionally) the given node."""
        variables = {'text': (lambda obj: {'xmltext': str(obj)}),
                     'num': (lambda xml_obj: int(xml_obj['xmltext']))}
        variables.update(machine_vars)
        variables.update(self.instr_vars)
        variables['group'] = match.group
        if node:
            variables.update({'node': node, '_': node.value})
        return eval(self.code, variables)


class Find(Instruction):
    """An instruction searching for nodes which are in the currently set
    relationship with the context node and match the predicate."""
    
    def __init__(self, expression, **instr_vars):
        """Save the expression in a textual and compiled version."""
        self._compile_code(expression, instr_vars)
    
    def execute(self, branch):
        """Find the nodes and return a list of branches which should replace
        the supplied branch."""
        new_branches = []
        for node in self._matching_nodes(branch):
            new_branch = branch.copy()
            for group in new_branch.groups:
                new_branch.match.group(group).add_node(node)
            new_branch.node = node
            new_branches.append(new_branch)
        return new_branches
    
    def _matching_nodes(self, branch):
        for node in branch.relation().search(branch.node):
            if self._evaluate_code(branch.vm.machine_vars, branch.match, node):
                yield node
    
    def __str__(self):
        """Return the string representation of the instruction."""
        return "FIND %s" % self.expression


class SetRelation(Instruction):
    """An instruction which sets the relation to be used for next search or
    node adding."""
    
    def __init__(self, relation):
        """The given relation argument should be a class."""
        self.relation = relation
    
    def execute(self, branch_or_vm):
        """Set the current relation of the branch / virtual machine."""
        branch_or_vm.relation = self.relation
    
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
        branch.match.groups().append(treepace.trees.Subtree())
    
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


class SearchReference(Instruction):
    """A back-reference to a numbered group in a search pattern."""
    
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
        return "SREF %d" % self.number


class AddNode(Instruction):
    """An instruction which adds the node to the correct position in the tree
    being built."""
    
    def __init__(self, expression, **instr_vars):
        """Save the expression in a textual and compiled version."""
        self._compile_code(expression, instr_vars)
    
    def execute(self, vm):
        """Create a new node, add it to the tree (or create a tree if it
        does not yet exist) and set it as the context node."""
        value = self._evaluate_code(vm.machine_vars, vm.match)
        node = vm.match.group().root.__class__(value)
        if not vm.tree:
            vm.tree = treepace.trees.Tree(node)
        else:
            vm.relation().build(vm.node, node)
        vm.node = node
    
    def __str__(self):
        """Return the string representation of the instruction."""
        return "ADD %s" % self.expression


class AddReference(Instruction):
    """A back-reference to a numbered group in a replacement."""
    
    def __init__(self, number):
        """Save the group number as an instruction argument."""
        self.number = number
    
    def execute(self, vm):
        """Add the given group's subtree to the tree and set its root
        as the context node.
        
        This may not seem intuitive when the 'child' relation is used
        immediately after the back-reference, but it is consistent.
        """
        tree = vm.match.group(self.number).to_tree()
        if not vm.tree:
            vm.tree = tree
        else:
            vm.relation().build(vm.node, tree.root)
        vm.node = tree.root
    
    def __str__(self):
        """Return the string representation of the instruction."""
        return "AREF %d" % self.number


class GoToParent(Instruction):
    """An instruction for navigation in the tree being built."""
    
    def execute(self, vm):
        """Change the context node to the current context node's parent."""
        vm.node = vm.node.parent
    
    def __str__(self):
        """Return the string representation of the instruction."""
        return "GPAR"
