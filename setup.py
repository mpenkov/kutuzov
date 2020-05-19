import io
import os.path
import setuptools


def get_version():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(curr_dir, 'kutuzov', 'version.py')) as fin:
        line = fin.readline().strip()
        parts = line.split(' ')
        assert len(parts) == 3
        assert parts[0] == '__version__'
        assert parts[1] == '='
        return parts[2].strip('\'"')


def read(fname):
    return io.open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()


#
# We cannot do "from smart_open.version import __version__" because that will
# require the dependencies for smart_open to already be in place, and that is
# not necessarily the case when running setup.py for the first time.
#
__version__ = get_version()

setuptools.setup(
    name='kutuzov',
    version=__version__,
    description='Derives type annotations from Sphinx comments in Python source',
    long_description=read('README.rst'),
    packages=setuptools.find_packages(),
    author='Michael Penkov',
    author_email='m@penkov.dev',
    url='https://github.com/mpenkov/kutuzov',
    download_url='http://pypi.python.org/pypi/kutuzov',
    keywords='sphinx pyannotate napoleon',
    license='MIT',
    platforms='any',
    python_requires=">=3.5.*",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
