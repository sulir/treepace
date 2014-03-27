from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

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

class RuleVisitor(NodeVisitor):
    def __init__(self):
        self.instructions = []
        self.start_num = 0
        self.end_num = 0
    
    def visit_any(self, node, visited_children):
        self._add('ANY')
    
    def visit_constant(self, node, visited_children):
        self._add('CONSTANT ' + node.text)
    
    def visit_code(self, node, visited_children):
        self._add('CODE ' + node.text[1:-1])
    
    def visit_reference(self, node, visited_children):
        self._add('REFERENCE %d' % int(node.text[1:]))
    
    def visit_group_start(self, node, visited_children):
        self.start_num += 1
        self.end_num = self.start_num
        self._add('GROUP_START %d' % self.start_num)
    
    def visit_group_end(self, node, visited_children):
        self._add('GROUP_END %d' % self.end_num)
        self.end_num -= 1
    
    def visit_relation(self, node, visited_children):
        self._add('RELATION %s' % node.text)
    
    def generic_visit(self, node, visited_children):
        pass
    
    def _add(self, instruction):
        self.instructions.append(instruction)

class Parser:
    def __init__(self):
        self._grammar = Grammar(GRAMMAR)
    
    def parse_pattern(self, pattern):
        ast = self._grammar['pattern'].parse(pattern)
        visitor = RuleVisitor()
        visitor.visit(ast)
        return visitor.instructions
