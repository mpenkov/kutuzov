import pytest

import kutuzov


@pytest.fixture
def f1():
    docstr = """
    :param int foo27: The foo

    :param str bar_prime: The bar
    :param package.submodule.type baz: The baz.
        It requires a multiline description.
    :returns: Whatever, we don't really care, only the type matters
    :rtype: package.submodule.Yolo
"""
    expected = [
        ('foo27', 'int'),
        ('bar_prime', 'str'),
        ('baz', 'package.submodule.type'),
        (None, 'package.submodule.Yolo'),
    ]
    return docstr, expected


def test_parse_sphinx_docstring(f1):
    docstr, expected = f1
    actual = kutuzov._parse_sphinx_docstring(docstr)
    assert expected == actual


def test_probe_function():

    def f(foo, bar, baz, undocumented):
        """
        :param int foo:
        :param float baz:
        :param str bar:
        :rtype: X
        """
        boz = None
        return boz

    expected = {
        'path': __file__,
        'func_name': 'f',
        'type_comments': ['(int str float Any) -> X'],
        'samples': 1,
    }

    #
    # Don't bother testing line numbers, they change far too often.
    #
    actual = kutuzov.probe_function(f)
    actual.pop('line')
    assert expected == actual


def test_probe_class():
    class Santa:
        def __init__(self, foo):
            """
            :param float foo:
            """

        def hohoho(self, foo):
            """
            :param int foo:
            :rtype: collections.defaultdict
            """

        @staticmethod
        def statik(bar):
            """
            :param float bar:
            """

        @classmethod
        def klass(cls, bar):
            """
            :param float bar:
            """

        @property
        def prop(self):
            """
            :rtype: int
            """

    expected = [
        {
            'path': __file__,
            'func_name': 'Santa.__init__',
            'type_comments': ['(float) -> None'],
            'samples': 1,
        },
        {
            'path': __file__,
            'func_name': 'hohoho',
            'type_comments': ['(int) -> collections.defaultdict'],
            'samples': 1,
        },
        {
            'path': __file__,
            'func_name': 'statik',
            'type_comments': ['(float) -> None'],
            'samples': 1,
        },
        {
            'path': __file__,
            'func_name': 'klass',
            'type_comments': ['(float) -> None'],
            'samples': 1,
        },
    ]

    actual = kutuzov.probe_class(Santa)
    for x in actual:
        x.pop('line')

    def f(d):
        return d['func_name']

    assert sorted(expected, key=f) == sorted(actual, key=f)
