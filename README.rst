What?
-----

Extracts type annotations from Python source documented with Sphinx-compatible docstrings.

Why?
----

Existing tools like `PyAnnotate <https://github.com/dropbox/pyannotate>`_ require you to write a driver to exercise your application, while a special hook collects type information and converts it to annotations.
This works really well, but requires significant effort in writing a comprehensive driver that covers your entire application.

If your application already has type information in its docstrings, it may be simpler to convert that information to annotations directly.
Kutuzov will help you with that.

How?
----

Kutuzov does this:

- Scans packages and submodules for docstrings
- Parses the docstrings, extracts type information about each parameter
- Writes a PyAnnotate-compatible JSON file

What remains for you is:

- Run PyAnnotate and consume the generated JSON file
- Tweak the results by hand
- PROFIT

The amount of tweaking you have to do may vary.
It significantly depends on the quality and accuracy of your docstrings.

Example
^^^^^^^

We will be annotating the example.py file.
You will need pyannotate (``pip install pyannotate``) to proceed.

.. code-block::

    $ python -m kutuzov example.py > type_info.json
    $ cat type_info.json
    [
        {
            "func_name": "Dog.__init__",
            "line": 2,
            "path": "example.py",
            "samples": 1,
            "type_comments": [
                "(str) -> None"
            ]
        },
        {
            "func_name": "Dog.bark",
            "line": 16,
            "path": "example.py",
            "samples": 1,
            "type_comments": [
                "(str) -> str"
            ]
        }
    ]
    $ pyannotate example.py --py3
    Refactored example.py
    --- example.py  (original)
    +++ example.py  (refactored)
    @@ -1,5 +1,5 @@
     class Dog:
    -    def __init__(self, name):
    +    def __init__(self, name: str) -> None:
             """
             :param str name: The name of this dog.
             """
    @@ -13,7 +13,7 @@
             """
             return self._name

    -    def bark(self, language='en'):
    +    def bark(self, language: str = 'en') -> str:
             """
             Make some noise!

    Files that need to be modified:
    example.py
    NOTE: this was a dry run; use -w to write files

You may have noticed that [example.py](example.py) already contains a PyAnnotate driver in the mainline.

.. code-block::

    $ cat type_info.json 
    [
        {
            "path": "example.py",
            "line": 2,
            "func_name": "Dog.__init__",
            "type_comments": [
                "(str) -> None"
            ],
            "samples": 1
        },
        {
            "path": "example.py",
            "line": 8,
            "func_name": "name",
            "type_comments": [
                "() -> str"
            ],
            "samples": 1
        },
        {
            "path": "example.py",
            "line": 16,
            "func_name": "Dog.bark",
            "type_comments": [
                "(str) -> str"
            ],
            "samples": 1
        }
    ]

If you compare that to the previously generated JSON, you will see that it is mostly similar.
The greatest difference is that Kutuzov missed the ``name`` property - it doesn't know how to handle those yet.

What's in a name?
-----------------

`Mikhail Kutuzov <https://en.wikipedia.org/wiki/Mikhail_Kutuzov>`_ was a contemporary of `Napoleon Bonaparte <https://en.wikipedia.org/wiki/Napoleon>`_.
A `particular painting <https://en.wikipedia.org/wiki/Bonaparte_Before_the_Sphinx>`__ depicts Napoleon before the Sphinx.
And `Sphinx <https://www.sphinx-doc.org/en/stable/>`_, of course, is the project that we all love for our Python documentation needs.

This project was partially inspired by `sphinx.ext.napoleon <https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`_, which does something similar, but for a different docstring format.
