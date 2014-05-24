"""Utility functions and mix-in classes."""
import builtins
from urllib.parse import quote_plus

class EqualityMixin:
    """Equality and inequality operator overloading based on attributes."""
    
    def __eq__(self, other):
        """All instance attributes are compared for equality."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            raise NotImplemented
    
    def __ne__(self, other):
        """Just a negation of the equality result."""
        return not self.__eq__(other)


class ReprMixin:
    """Default string and debugging representations of objects."""
    
    def __str__(self):
        """Ideally, subclasses should supply their own implementations."""
        return str(self.__dict__)
    
    def __repr__(self):
        """The debug representation is automatically derived from the string
        representation by adding a class name and a unique identifier."""
        identifier = hex(id(self))[2:]
        return "<%s '%s' @%s>" % (self.__class__.__name__, self, identifier)


class IPythonDotMixin:
    """A graphical and HTML representation for IPython Notebook.
    
    Derived classes should implement _repr_dot_() method returning a source
    code in DOT graph specification language.
    """
    
    def _repr_png_(self):
        from IPython.core.display import Image
        return Image(url=self._url())._repr_png_()
    
    def _repr_html_(self):
        from IPython.core.display import Image
        return Image(url=self._url())._repr_html_()
    
    def _url(self):
        url = 'https://chart.googleapis.com/chart?cht=gv&chl='
        return url + quote_plus(self._repr_dot_()) + '&ext=.png'


class IPythonFormatter:
    """An HTML representation of lists whose items have HTML representation."""
    
    def __init__(self):
        """Find if IPython is running."""
        self.is_ipython = hasattr(builtins, '__IPYTHON__')
    
    def register(self):
        """Register the formatter."""
        if self.is_ipython:
            from IPython import get_ipython
            formatter = get_ipython().display_formatter.formatters['text/html']
            formatter.for_type(list, self._list_to_html)
    
    def _list_to_html(self, array):
        if not array or any(not hasattr(item, '_repr_html_') for item in array):
            return None
        
        TD = '<td style="border: none; %s">%s</td>'
        BRACKET = '<td style="border-width: %s; width: 20px;"></td>'
        
        html = '<table style="border: none;"><tr style="border: none">'
        html += BRACKET % '2px 0px 2px 2px'
        for index, item in enumerate(array):
            html += TD % ('padding: 8px 0 5px 0;', item._repr_html_())
            if index < len(array) - 1:
                html += TD % ('vertical-align: bottom; font-size: 35px;',
                              ',&nbsp;')
        return html + (BRACKET % '2px 2px 2px 0px') + '</tr></table>'
