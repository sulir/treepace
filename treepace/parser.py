"""A parser of transformation rule strings."""

import re
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from treepace.machine import Find, GroupEnd, GroupStart, Reference, Relation

GRAMMAR = '''
    rule          = pattern '->' replacement
    _             = ~r'[ \t]*'
    
    pattern       = group (relation group)*
    group         = node / (group_start pattern group_end)
    node          = any / constant / code / reference
    any           = _'.'_
    constant      = (_~r'[-\w]*\w'_) / (_'"' ~r'[^"]+' '"'_)
    code          = _'[' python_expr+ ']'_
    python_expr   = ~r'[^\[\]]+' / ('[' python_expr ']')
    reference     = _~r'\$[0-9]+'_
    group_start   = _'{'_
    group_end     = _'}'_
    relation      = child / sibling / next_sibling / parent
    child         = _'<'_
    sibling       = _'&'_
    next_sibling  = _','_
    parent        = _'>'_
    
    replacement   = repl_node (repl_relation repl_node)*
    repl_node     = constant / code / reference
    repl_relation = child / next_sibling / parent
'''

class InstructionGenerator(NodeVisitor):
    """A post-order visitor which generates a list of virtual machine
    instructions from an AST."""
    
    def __init__(self):
        self.instructions = []
        self._start_num = 0
        self._end_num = 0
    
    def visit_any(self, node, visited_children):
        self._add(Find('True'))
    
    def visit_constant(self, node, visited_children):
        text = re.search('"?(.*)"?', node.text.strip()).group(1)
        self._add(Find('str(_) == str(%s)' % repr(text)))
    
    def visit_code(self, node, visited_children):
        self._add(Find(node.text.strip()[1:-1]))
    
    def visit_reference(self, node, visited_children):
        self._add(Reference(int(node.text.replace('$', ''))))
    
    def visit_group_start(self, node, visited_children):
        self._start_num += 1
        self._end_num = self._start_num
        self._add(GroupStart(self._start_num))
    
    def visit_group_end(self, node, visited_children):
        self._add(GroupEnd(self._end_num))
        self._end_num -= 1
    
    def visit_child(self, node, visited_children):
        self._add(Relation(Relation.CHILD))
    
    def visit_sibling(self, node, visited_children):
        self._add(Relation(Relation.SIBLING))
    
    def visit_next_sibling(self, node, visited_children):
        self._add(Relation(Relation.NEXT_SIB))
    
    def visit_parent(self, node, visited_children):
        self._add(Relation(Relation.PARENT))
    
    def generic_visit(self, node, visited_children):
        pass
    
    def _add(self, instruction):
        self.instructions.append(instruction)


class Parser:
    """A parser of rule, pattern and replacement strings."""
    
    def __init__(self):
        """Initialize the parser by compiling the grammar to be used by
        a parser generator."""
        self._grammar = Grammar(GRAMMAR)
    
    def parse_pattern(self, pattern):
        """Parse the pattern and return an instruction list."""
        ast = self._grammar['pattern'].parse(pattern)
        generator = InstructionGenerator()
        generator.visit(ast)
        return generator.instructions
