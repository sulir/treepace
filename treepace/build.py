"""A replacement tree constructing virtual machine."""

from treepace.utils import ReprMixin

class BuildMachine(ReprMixin):
    """A machine which builds a tree which will be used as a replacement
    during the transformation."""
    
    def __init__(self, match, instructions, variables):
        """Initialize the VM with the default state."""
        self.match = match
        self.instructions = instructions
        self.node = None
        self.relation = None
        self.tree = None
        self.machine_vars = variables
    
    def __str__(self):
        """Return the machine state in a form of a string."""
        return "match: %s, instructions: %s" % (self.match,
            list(map(str, self.instructions)))
    
    def build(self):
        """Execute all instructions and return the built tree."""
        while self.instructions:
            self.instructions.pop(0).execute(self)
        return self.tree
