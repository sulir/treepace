import unittest
from treepace.compiler import Compiler
from treepace.machine import Find, GroupEnd, GroupStart, Reference, SetRelation
from treepace.relations import Child, NextSibling

class TestCompiler(unittest.TestCase):
    def test_compile_pattern(self):
        result = Compiler().compile_pattern('{.} < [False], $1')
        expected = [GroupStart(1), Find('True'), GroupEnd(1),
                    SetRelation(Child), Find('False'),
                    SetRelation(NextSibling), Reference(1)]
        self.assertEqual(result, expected)
