import unittest
from treepace.parser import Parser
from treepace.machine import Find, GroupEnd, GroupStart, Reference, Relation

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
    
    def test_parse_pattern(self):
        result = self.parser.parse_pattern('{.} < [False], $1')
        expected = [GroupStart(1), Find('True'), GroupEnd(1),
                    Relation(Relation.CHILD), Find('False'),
                    Relation(Relation.NEXT_SIB), Reference(1)]
        self.assertEqual(result, expected)
