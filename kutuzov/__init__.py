import importlib.util
import inspect
import io
import json
import re
import sys

from typing import (
    Dict,  # TypedDict unavailable before Py3.8
    Callable,
    List,
    Tuple,
)


def parse_sphinx_docstring(docstr: str) -> Tuple[str, str]:
    def g():
        for line in docstr.split('\n'):
            match = re.search(r':param (?P<type>[\w.]+) (?P<name>\w+):', line)
            if match:
                yield match.group('name'), match.group('type')

            match = re.search(r':rtype: (?P<type>[\w.]+)$', line)
            if match:
                yield None, match.group('type')

    return list(g())


def probe_function(f) -> Dict:
    if not (hasattr(f, '__doc__') and f.__doc__):
        return None

    param_types = dict(parse_sphinx_docstring(f.__doc__))
    buf = io.StringIO()
    buf.write('(')

    for param_name in f.__code__.co_varnames[:f.__code__.co_argcount]:
        if param_name in ('self', 'cls'):
            #
            # TODO: how to handle these?
            #
            continue

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


def probe_class(klass) -> List[Dict]:
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
                info = probe_function(thing)
            else:
                info = None

            if info:
                yield info

    return list(g())


def probe_file(file_path: str) -> List[Dict]:
    #
    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    #
    module_name = 'dummy'
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return probe_module(module)


def probe_module(module) -> List[Dict]:
    if isinstance(module, str):
        module = importlib.import_module(module)

    # import pdb;pdb.set_trace()

    def g():
        for attr in dir(module):
            thing = getattr(module, attr)

            if inspect.isfunction(thing):
                if module.__file__ == thing.__code__.co_filename:
                    probe = probe_function
                else:
                    probe = None
            elif inspect.isclass(thing):
                probe = probe_class
            else:
                probe = None

            if probe:
                info = probe(thing)
            else:
                info = None

            if info:
                yield info

    return list(g())


def main():
    info = probe_module(sys.argv[1])
    json.dump(info, sys.stdout, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
