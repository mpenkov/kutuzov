import functools

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


@pytest.fixture
def f2():
    docstr = """Open the URI object, returning a file-like object.

    Parameters
    ----------
    uri: str or object
        The object to open.
    mode: str, optional
        Mimicks built-in open parameter of the same name.
    buffering: int, optional
        Mimicks built-in open parameter of the same name.
    encoding: str, optional
        Mimicks built-in open parameter of the same name.
    errors: str, optional
        Mimicks built-in open parameter of the same name.
    newline: str, optional
        Mimicks built-in open parameter of the same name.
    closefd: boolean, optional
        Mimicks built-in open parameter of the same name.  Ignored.
    opener: object, optional
        Mimicks built-in open parameter of the same name.  Ignored.
    ignore_ext: boolean, optional
        Disable transparent compression/decompression based on the file extension.
    transport_params: dict, optional
        Additional parameters for the transport layer (see notes below).

    Returns
    -------
    A file-like object.
"""
    expected = [
        ('uri', 'str'),
        ('mode', 'str'),
        ('buffering', 'int'),
        ('encoding', 'str'),
        ('errors', 'str'),
        ('newline', 'str'),
        ('closefd', 'bool'),
        ('opener', 'object'),
        ('ignore_ext', 'bool'),
        ('transport_params', 'dict'),
    ]
    return docstr, expected


def test_parse_sphinx_docstring(f1):
    docstr, expected = f1
    actual = kutuzov._parse_sphinx_docstring(docstr)
    assert expected == actual


def test_parse_gensim_docstring(f2):
    docstr, expected = f2
    actual = kutuzov._parse_gensim_docstring(docstr)
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
            'func_name': 'Santa.hohoho',
            'type_comments': ['(int) -> collections.defaultdict'],
            'samples': 1,
        },
        {
            'path': __file__,
            'func_name': 'Santa.statik',
            'type_comments': ['(float) -> None'],
            'samples': 1,
        },
        {
            'path': __file__,
            'func_name': 'Santa.klass',
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


def my_decorator(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        print('inner')
        return f(*args, **kwargs)
    return inner


@my_decorator
def decorated_function(foo, bar, baz='boz'):
    """
    :param int foo:
    :param float bar:
    :param str baz:
    :rtype: bool
    """


def test_probe_decorated_function():
    expected = {
        'path': __file__,
        'func_name': 'decorated_function',
        'type_comments': ['(int float str) -> bool'],
        'samples': 1,
    }

    actual = kutuzov.probe_function(decorated_function)
    actual.pop('line')

    assert expected == actual
