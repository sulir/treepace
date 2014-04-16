"""Tree node relations."""

import treepace.trees

class Child:
    """A child relation."""
    
    def search(self, node):
        return node.children


class Sibling:
    """All siblings (excluding the node itself)."""
    
    def search(self, node):
        if node.parent:
            return filter(lambda x: x != node, node.parent.children)


class NextSibling:
    """An immediately following sibling."""
    
    def search(self, node):
        next_index = node.index + 1
        if node.parent and len(node.parent.children) > next_index:
            return [node.parent.children[next_index]]
        else:
            return []
    
    def build(self, context, node):
        context.parent.insert_child(node, context.index + 1)


class Parent:
    """A parent relation."""
    
    def search(self, node):
        return [node.parent] if node.parent else []
    
    def build(self, context, node):
        context.add_child(node)


class Descendant:
    """A descendant or the node itself."""
    
    def search(self, node):
        return treepace.trees.Tree(node).preorder()
