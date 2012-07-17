#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from r3.version import __version__

setup(
    name = 'r3',
    version = __version__,
    description = "r3 is a map-reduce engine written in python",
    long_description = """
r3 is a map-reduce engine that uses redis as a backend. It's very simple to use.
""",
    keywords = 'map reduce',
    author = 'Bernardo Heynemann',
    author_email = 'heynemann@gmail.com',
    url = 'http://heynemann.github.com/r3/',
    license = 'MIT',
    classifiers = ['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Operating System :: MacOS',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
    ],

    include_package_data = True,
    package_data = {
        '': ['*.gif', '*.png', '*.jpg', '*.jpeg', '*.css', '*.js', '*.html'],
    },

    packages = ['r3', 'r3'],
    package_dir = {"r3": "r3"},

    install_requires=[
        'redis',
        'tornado-redis',
        'tornado',
        'ujson',
        'flask',
        'argparse'
    ],

    entry_points = {
        'console_scripts': [
            'r3-app=r3.app.server:main',
            'r3-web=r3.web.server:main',
            'r3-map=r3.worker.mapper:main'
        ],
    }
)

