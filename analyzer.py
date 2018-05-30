"""Analyze the HTML document
"""

import re
import bs4

class Pattern:
    """Check if the document have a specific pattern"""
    def search(self, document):
        """Search through the document
            document: str, or iterable of str
        """
        raise NotImplementedError

    def __add__(self, other):
        return OrPattern(self, other)
    
    def __mul__(self, other):
        return AndPattern(self, other)
    
    def __lsub__(self, other):
        return SubPattern(self, other)

class TruePattern(Pattern):
    def search(self, document):
        return True


class FalsePattern(Pattern):
    def search(self, document):
        return None


class AndPattern(Pattern):
    def __init__(self, *patterns):
        self.patterns = patterns
    
    def search(self, document):
        res = None
        for pattern in self.patterns:
            res = pattern.search(document)
            if res is None:
                return None
        return res

class OrPattern(Pattern):
    def __init__(self, *patterns):
        self.patterns = patterns
    
    def search(self, document):
        for pattern in self.patterns:
            res = pattern.search(document)
            if res is not None:
                return res
        return None

class SubPattern(Pattern):
    def __init__(self, ours, others):
        self.ours = ours
        self.others = others
    
    def search(self, document):
        res = self.ours.search(document)
        if res is None:
            return None
        else:
            res_t = self.others.search(document)
            if res_t:
                return None
            else:
                return res

class Contains(Pattern):
    """Check if a document contains a specific word"""
    def __init__(self, word):
        self.word = word
    
    def search(self, document):
        if isinstance(document, str):
            res = document.find(self.word)
            if res == -1:
                return
            else:
                return res
        else:
            try:
                for line in document:
                    res = line.find(self.word)
                    if res != -1:
                        return res
                return None
            except Exception:
                print("ERROR: Expect str, or str iterable ,got {}".format(document.__module__ + '.' + document.__name__))

def filter_tag(tag):
    """Limit search to the inner text of specific tags"""
    def fun(OldPattern):
        class anon_class(Pattern):
            def __init__(self, *args, **kwargs):
                self.pattern = OldPattern(*args, **kwargs)

            def search(self, document):
                html = bs4.BeautifulSoup(document, "html5lib")
                for elem in html.find_all(tag):
                    if self.pattern.search(elem.get_text()) is not None:
                        return True
                return False
        return anon_class
    return fun

@filter_tag('title')
class TitleContains(Contains):
    pass


if __name__ == '__main__':
    doc = ["hello", "world"]
    docstr = "hello world babe"
    x = Contains("hello")
    y = Contains("babe")
    xpy = x + y
    xmy = x * y
    print(doc, "xpy", xpy.search(doc))
    print(doc, "xmy", xmy.search(doc))
    print(docstr, "xpy", xpy.search(docstr))
    print(docstr, "xmy", xmy.search(docstr))

