import unittest
from treepace.compiler import Compiler
from treepace.instructions import (AddNode, AddReference, Find, GoToParent,
    GroupEnd, GroupStart, SearchReference, SetRelation)
from treepace.relations import Child, NextSibling

class TestCompiler(unittest.TestCase):
    def test_compile_pattern(self):
        result = Compiler.compile_pattern('{.} < [False], $1')
        expected = [GroupStart(1), Find('True'), GroupEnd(1),
                    SetRelation(Child), Find('False'),
                    SetRelation(NextSibling), SearchReference(1)]
        self.assertEqual(result, expected)
    
    def test_compile_replacement(self):
        result = Compiler.compile_replacement('a < "\'s", [a[0]], $0>')
        expected = [AddNode("'a'"), SetRelation(Child), AddNode('"\'s"'),
                    SetRelation(NextSibling), AddNode('a[0]'),
                    SetRelation(NextSibling), AddReference(0), GoToParent()]
        self.assertEqual(result, expected)
