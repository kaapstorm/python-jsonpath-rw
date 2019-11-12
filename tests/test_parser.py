from __future__ import unicode_literals, print_function, absolute_import, division, generators, nested_scopes
import unittest

from jsonpath_rw.lexer import JsonPathLexer
from jsonpath_rw.parser import JsonPathParser
from jsonpath_rw.jsonpath import *

class TestParser(unittest.TestCase):
    # TODO: This will be much more effective with a few regression tests and `arbitrary` parse . pretty testing

    @classmethod
    def setup_class(cls):
        logging.basicConfig()

    def check_parse_cases(self, test_cases):
        parser = JsonPathParser(debug=True, lexer_class=lambda:JsonPathLexer(debug=False)) # Note that just manually passing token streams avoids this dep, but that sucks

        for string, parsed in test_cases:
            print(string, '=?=', parsed) # pytest captures this and we see it only on a failure, for debugging
            assert parser.parse(string) == parsed

    def test_atomic(self):
        self.check_parse_cases([('foo', Fields('foo')),
                                ('*', Fields('*')),
                                ('baz,bizzle', Fields('baz','bizzle')),
                                ('[1]', Index(1)),
                                ('[1:]', Slice(start=1)),
                                ('[:]', Slice()),
                                ('[*]', Slice()),
                                ('[:2]', Slice(end=2)),
                                ('[1:2]', Slice(start=1, end=2)),
                                ('[5:-2]', Slice(start=5, end=-2))
                               ])

    def test_nested(self):
        self.check_parse_cases([('foo.baz', Child(Fields('foo'), Fields('baz'))),
                                ('foo.baz,bizzle', Child(Fields('foo'), Fields('baz', 'bizzle'))),
                                ('foo where baz', Where(Fields('foo'), Fields('baz'))),
                                ('foo..baz', Descendants(Fields('foo'), Fields('baz'))),
                                ('foo..baz.bing', Descendants(Fields('foo'), Child(Fields('baz'), Fields('bing'))))])

    def test_goessner_examples(self):
        # Examples taken from https://goessner.net/articles/JsonPath/
        self.check_parse_cases([
            ("$.store.book[0].title", Child(Child(Child(Child(Root(), Fields('store')), Fields('book')), Index(0)), Fields('title'))),
            ("$['store']['book'][0]['title']", Child(Child(Child(Child(Root(), Fields('store')), Fields('book')), Index(0)), Fields('title'))),
            # ("$.store.book[(@.length-1)].title", None),
            # ("$.store.book[?(@.price < 10)].title", None),
            ("$.store.book[*].author", Child(Child(Child(Child(Root(), Fields('store')), Fields('book')), Slice()), Fields('author'))),
            ("$..author", Descendants(Root(), Fields('author'))),
            ("$.store.*", Child(Child(Root(), Fields('store')), Fields('*'))),
            ("$.store..price", Descendants(Child(Root(), Fields('store')), Fields('price'))),
            ("$..book[2]", Child(Descendants(Root(), Fields('book')), Index(2))),
            # ("$..book[(@.length-1)]", None),
            ("$..book[-1:]", Child(Descendants(Root(), Fields('book')), Slice(start=-1))),
            # ("$..book[0,1]", None),
            ("$..book[:2]", Child(Descendants(Root(), Fields('book')), Slice(end=2))),
            # ("$..book[?(@.isbn)]", None),
            # ("$..book[?(@.price<10)]", None),
            ("$..*", Descendants(Root(), Fields('*'))),
        ])
