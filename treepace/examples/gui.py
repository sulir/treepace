import time
from tkinter import BOTH, LEFT, Text, Tk, messagebox
from tkinter.ttk import Frame, Treeview, Button
from treepace import Node, Tree
from tkinter.constants import END
from treepace.formats import IndentedText

class GuiNode(Node):
    def __init__(self, value, children=[]):
        if self.tv.exists('root'):
            self.id = self.tv.insert('root', 'end', text=str(value))
            self.tv.detach(self.id)
        else:
            self.id = self.tv.insert('', 0, 'root', text=str(value))
        super().__init__(value, children)
    
    @Node.value.setter
    def value(self, _value):
        self.tv.see(self.id)
        self.tv.selection_set(self.id)
        self._pause()
        self._value = _value
        self.tv.item(self.id, text=str(_value))
        self._pause()
    
    def insert_child(self, child, index):
        self.tv.selection_set(self.id)
        self._pause()
        super().insert_child(child, index)
        self.tv.move(child.id, self.id, index)
        self.tv.see(child.id)
        self.tv.selection_set(child.id)
        self._pause()
    
    def detach(self):
        self.tv.selection_set(self.parent.id)
        self._pause()
        super().detach()
        self.tv.detach(self.id)
        self._pause()
    
    def __del__(self):
        try:
            if self.parent and not self._children:
                self.tv.delete(self.id)
        except Exception:
            pass
    
    def _pause(self):
        for _ in range(5):
            time.sleep(.1)
            GuiNode.tv.update()


class Window(Tk):
    def __init__(self):
        super().__init__()
        self.title('Treepace Tree Transformation GUI Demo')
        self.geometry('640x400')
        self.resizable(False, False)
        self.tree_frame = Frame()
        self.tree_button = Button(self.tree_frame, text="Load tree",
                                  command=self.load)
        self.tree_button.pack(expand=True, fill=BOTH)
        self.tree_text = Text(self.tree_frame, width=20)
        self.tree_text.pack(expand=True, fill=BOTH)
        self.tree_text.insert('1.0', DEFAULT_TREE)
        self.tree_frame.pack(side=LEFT, expand=True, fill=BOTH)
        
        self.program_frame = Frame()
        self.program_button = Button(self.program_frame, text="Transform",
                                     command=self.transform)
        self.program_button.pack(expand=True, fill=BOTH)
        self.program_text = Text(self.program_frame, width=60, height=8)
        self.program_text.pack(expand=True, fill=BOTH)
        self.program_text.insert('1.0', DEFAULT_PROGRAM)
        self.tv = Treeview(self.program_frame)
        self.tv.pack(expand=True, fill=BOTH)
        self.program_frame.pack(side=LEFT, expand=True, fill=BOTH)

        GuiNode.tv = self.tv
        self.load()
    
    def load(self):
        if self.tv.exists('root'):
            self.tv.delete('root')
        program = self.tree_text.get('1.0', END)
        self.tree = Tree.load(program, IndentedText, GuiNode)
    
    def transform(self):
        try:
            self.tree.transform(self.program_text.get('1.0', END))
        except Exception as e:
            messagebox.showerror("Transformation error", e)

DEFAULT_TREE = '''\
min
    2
    min
        min
            1
            3
        4'''

DEFAULT_PROGRAM = 'min < {[_.isdigit()]}, {[_.isdigit()]} -> [min($1, $2)]'

if __name__ == '__main__':
    Window().mainloop()
