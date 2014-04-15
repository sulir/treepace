"""A parser and instruction generator for transformation rule strings."""

import re
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from treepace.machine import Find, GroupEnd, GroupStart, Reference, SetRelation
from treepace.relations import Child, NextSibling, Parent, Sibling

GRAMMAR = Grammar('''
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
    repl_node     = repl_constant / repl_code / repl_ref
    repl_constant = constant
    repl_code     = code
    repl_ref      = reference
    repl_relation = child / next_sibling / parent
''')

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
        text = self._text_constant(node)
        self._add(Find('str(_.value) == str(%s)' % repr(text)))
    
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
        self._add(SetRelation(Child))
    
    def visit_sibling(self, node, visited_children):
        self._add(SetRelation(Sibling))
    
    def visit_next_sibling(self, node, visited_children):
        self._add(SetRelation(NextSibling))
    
    def visit_parent(self, node, visited_children):
        self._add(SetRelation(Parent))
    
    def generic_visit(self, node, visited_children):
        pass
    
    def _add(self, instruction):
        self.instructions.append(instruction)
    
    def _text_constant(self, node):
        return re.search('"?(.*)"?', node.text.strip()).group(1)

class Compiler:
    """A compiler from rule, pattern and replacement strings to instructions."""
    
    def compile_pattern(self, pattern):
        """Parse the pattern and return an instruction list."""
        return self._compile('pattern', pattern)
    
    def compile_rule(self, rule):
        """Parse the pattern and return an instruction list."""
        return self._compile('rule', rule)
    
    def _compile(self, rule_name, string):
        ast = GRAMMAR[rule_name].parse(string)
        generator = InstructionGenerator()
        generator.visit(ast)
        return generator.instructions
