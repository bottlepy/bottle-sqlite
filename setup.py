#!/usr/bin/env python

import sys
import os
from setuptools import setup

# This ugly hack executes the first few lines of the module file to look up some
# common variables. We cannot just import the module because it depends on other
# modules that might not be installed yet.
filename = os.path.join(os.path.dirname(__file__), 'bottle_sqlite.py')
with open(filename) as fp:
    source = fp.read().split('### CUT HERE')[0]
exec(source)

setup(
    name = 'bottle-sqlite',
    version = __version__,
    url = 'https://github.com/bottlepy/bottle-sqlite',
    description = 'SQLite3 integration for Bottle.',
    long_description = __doc__,
    author = 'Marcel Hellkamp',
    author_email = 'marc@gsites.de',
    license = __license__,
    platforms = 'any',
    py_modules = [
        'bottle_sqlite'
    ],
    requires = [
        'bottle (>=0.12)'
    ],
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
