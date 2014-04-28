"""A parser and instruction generator for transformation rule strings."""

from functools import lru_cache
import re
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from treepace.instructions import (AddNode, AddReference, Find, GoToParent,
    GroupEnd, GroupStart, SearchReference, SetRelation)
from treepace.relations import Child, NextSibling, Parent, Sibling

GRAMMAR = Grammar('''
    rule          = pattern '->' replacement
    _             = (' ' / '\t')*
    
    pattern       = group rel_group*
    group         = node / (group_start pattern group_end)
    rel_group     = (relation group) / parent_any
    node          = any / constant / code / reference
    any           = _'.'_
    constant      = _((~r'\w'+) / ('"' (!'"' ~'.')+ '"'))_ 
    code          = _'[' python_code ']'_
    python_code   = expr_part+
    expr_part     = (!('[' / ']') ~'.')+ / ('[' expr_part ']')
    reference     = _ '$' reference_num _
    reference_num = ~r'\d'+
    group_start   = _'{'_
    group_end     = _'}'_
    relation      = child / sibling / next_sibling
    child         = _'<'_
    sibling       = _'&'_
    next_sibling  = _','_
    parent_any    = _'>'_
    
    replacement   = repl_node repl_rel_node*
    repl_node     = constant / code / reference
    repl_rel_node = (repl_relation node) / parent_any
    repl_relation = child / next_sibling
''')

class Compiler:
    """A compiler from rule, pattern and replacement strings to instructions."""
    
    @staticmethod
    @lru_cache()
    def compile_pattern(pattern):
        """Parse the pattern and return an instruction list."""
        return SearchGenerator().visit(GRAMMAR['pattern'].parse(pattern))
    
    @staticmethod
    @lru_cache()
    def compile_replacement(replacement):
        """Parse the replacement and return an instruction list."""
        ast = GRAMMAR['replacement'].parse(replacement)
        return BuildGenerator().visit(ast)
    
    @staticmethod
    @lru_cache()
    def compile_rule(rule):
        """Parse the rule and return two instruction lists -- searching
        instructions and replacing instructions."""
        ast = GRAMMAR['rule'].parse(rule)
        search_instructions = SearchGenerator().visit(ast.children[0])
        replace_instructions = BuildGenerator().visit(ast.children[2])
        return (search_instructions, replace_instructions)


class InstructionGenerator(NodeVisitor):
    """A base class with common behavior for post-order visitors which
    generate a list of virtual machine instructions from an AST."""
    
    def __init__(self):
        """Initialize the instruction list and a level counter."""
        self._instructions = []
        self._child_level = 0
    
    def generic_visit(self, node, visited_children):
        """Just continue with the traversal."""
        pass
    
    def visit_child(self, node, visited_children):
        """Add the instruction 'REL child'."""
        self._add(SetRelation(Child))
        self._child_level += 1
    
    def visit_next_sibling(self, node, visited_children):
        """Add the instruction 'REL next_sib'."""
        self._add(SetRelation(NextSibling))
    
    def _add(self, instruction):
        self._instructions.append(instruction)
    
    def _check_child_level(self):
        if self._child_level < 0:
            raise CompileError('Too many parent relations')
    
    def _text_constant(self, node):
        return repr(re.search('"?([^"]*)"?', node.text.strip()).group(1))


class SearchGenerator(InstructionGenerator):
    """A generator of tree-searching instructions."""
    
    def __init__(self):
        """Initialize the group counters."""
        super().__init__()
        self._started_group = 0
        self._ended_groups = set()
    
    def visit_pattern(self, node, visited_children):
        """Return the generated instruction list (at the top of the AST)."""
        return self._instructions
    
    def visit_any(self, node, visited_children):
        """Add an instruction which matches any node."""
        self._add(Find('True'))
    
    def visit_constant(self, node, visited_children):
        """Add an instruction which matches the constant."""
        self._add(Find('str(_) == str(%s)' % self._text_constant(node)))
    
    def visit_python_code(self, node, visited_children):
        """Add an instruction which matches the predicate."""
        self._add(Find(node.text))
    
    def visit_reference_num(self, node, visited_children):
        """Add a back-referencing instruction."""
        group_num = int(node.text)
        if group_num not in self._ended_groups:
            raise CompileError('Group %d cannot be referenced yet' % group_num)
        self._add(SearchReference(group_num))
    
    def visit_group_start(self, node, visited_children):
        """Add a group-starting instruction and adjust the counters."""
        self._started_group += 1
        self._add(GroupStart(self._started_group))
    
    def visit_group_end(self, node, visited_children):
        """Add a group-ending instruction and adjust the counter."""
        end = max(set(range(1, self._started_group + 1)) - self._ended_groups)
        self._ended_groups.add(end)
        self._add(GroupEnd(end))
    
    def visit_sibling(self, node, visited_children):
        """Add the instruction 'REL sibling'."""
        self._add(SetRelation(Sibling))
    
    def visit_parent_any(self, node, visited_children):
        """The 'parent' relation followed by an implicit 'any' pattern."""
        self._add(SetRelation(Parent))
        self._add(Find('True'))
        self._child_level -= 1
        self._check_child_level()


class BuildGenerator(InstructionGenerator):
    """A generator of instructions which build a replacement tree."""
    
    def visit_replacement(self, node, visited_children):
        """Return the generated instruction list (at the top of the AST)."""
        return self._instructions
    
    def visit_constant(self, node, visited_children):
        """Add an instruction which appends a node with a constant value
        to the tree."""
        self._add(AddNode(self._text_constant(node)))
    
    def visit_python_code(self, node, visited_children):
        """Add an instruction which appends a dynamically generated node
        to the tree."""
        self._add(AddNode(node.text))
    
    def visit_reference_num(self, node, visited_children):
        """Add a back-referencing instruction."""
        self._add(AddReference(int(node.text)))
    
    def visit_parent_any(self, node, visited_children):
        """Add an instruction which navigates up in the tree being built."""
        self._add(GoToParent())
        self._child_level -= 1
        self._check_child_level()


class CompileError(Exception):
    """Raised when a non-parser related error occurs during compilation."""
    pass
