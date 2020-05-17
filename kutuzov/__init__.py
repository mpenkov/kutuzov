import importlib.util
import inspect
import io
import re
import sys

from typing import (
    Dict,  # TypedDict unavailable before Py3.8
    Callable,
    List,
    Optional,
    Tuple,
)


def _parse_gensim_docstring(docstr: str) -> List[Tuple[str, str]]:
    """Extract keyword argument documentation from a function's docstring.

    Parameters
    ----------
    docstr
        The docstring to extract keyword arguments from.

    Returns
    -------
    list of (str, str)

    str
        The name of the parameter.
    str
        Its type.

    Notes
    -----
    The implementation is rather fragile.  It expects the following:

    1. The parameters are under an underlined Parameters section
    2. Keyword parameters have the literal ", optional" after the type
    3. Names and types are not indented
    4. Descriptions are indented with 4 spaces
    5. The Parameters section ends with an empty line.

    """
    if not docstr:
        return []

    lines = inspect.cleandoc(docstr).split('\n')

    #
    # 1. Find the underlined 'Parameters' section
    # 2. Once there, continue parsing parameters until we hit an empty line
    #
    while lines and lines[0] != 'Parameters':
        lines.pop(0)

    if not lines:
        return []

    lines.pop(0)
    lines.pop(0)

    retval = []
    while lines and lines[0]:
        name, type_ = lines.pop(0).split(':', 1)
        while lines and lines[0].startswith('    '):
            lines.pop(0)

        if ', optional' in type_:
            type_ = 'Optional[%s]' % type_.replace(', optional', '').strip()

        retval.append((name.strip(), type_.strip()))

    return retval


def _parse_sphinx_docstring(docstr: str) -> List[Tuple[str, str]]:
    def tweak_type(t):
        return t.replace('boolean', 'bool')

    def g():
        for line in docstr.split('\n'):
            match = re.search(r':param (?P<type>[\w.]+) (?P<name>\w+):', line)
            if match:
                yield match.group('name'), tweak_type(match.group('type'))

            match = re.search(r':rtype: (?P<type>[\w.]+)$', line)
            if match:
                yield None, tweak_type(match.group('type'))

    return list(g())


def _get_parser(flavor):
    if flavor == 'sphinx':
        return _parse_sphinx_docstring
    elif flavor == 'gensim':
        return _parse_gensim_docstring
    else:
        raise ValueError('unexpected flavor: %r' % flavor)


def probe_function(f: Callable, flavor: str = 'sphinx') -> Optional[Dict]:
    if not (hasattr(f, '__doc__') and f.__doc__):
        return None

    parser = _get_parser(flavor)

    param_types = dict(parser(f.__doc__))
    buf = io.StringIO()
    buf.write('(')

    for param_name in f.__code__.co_varnames[:f.__code__.co_argcount]:
        try:
            buf.write('%s ' % param_types[param_name])
        except KeyError:
            buf.write('Any ')
    buf.write(') -> %s' % param_types.get(None))

    return {
        'path': f.__code__.co_filename,
        'line': f.__code__.co_firstlineno,
        'func_name': f.__name__,
        'samples': 1,
        'type_comments': [buf.getvalue().replace(' )', ')')],
    }


def probe_class(klass, flavor: str = 'sphinx') -> List[Dict]:
    assert inspect.isclass(klass)

    def g():
        for attr in dir(klass):
            if attr.startswith('_') and attr != '__init__':
                continue

            try:
                thing = getattr(klass, attr)
            except Exception as e:
                #
                # This can happen when touching something that requires
                # prior init, e.g. mongoengine.Document.objects requires an
                # existing connection to a DB.
                #
                continue

            is_callable = inspect.isfunction(thing) or inspect.ismethod(thing)

            #
            # Don't bother probing things defined in other modules, as they
            # are likely from superclasses.
            #
            if is_callable and thing.__module__ == klass.__module__:
                info = probe_function(thing, flavor=flavor)
            else:
                info = None

            if info:
                yield info

    return list(g())


def probe_module(module, flavor: str = 'sphinx') -> List[Dict]:
    if isinstance(module, str):
        module = importlib.import_module(module)

    def g():
        for attr in dir(module):
            thing = getattr(module, attr)

            if inspect.isfunction(thing):
                if module.__file__ == thing.__code__.co_filename:
                    info = probe_function(thing, flavor=flavor)
                    if info:
                        yield info
            elif inspect.isclass(thing):
                for info in probe_class(thing, flavor=flavor):
                    if info:
                        yield info

    return sorted(g(), key=lambda x: x['line'])
