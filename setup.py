#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.7',
    'records==0.5.2',
    'attrdict==2.0.0',
]

setup_requirements = [
    'pytest-runner',
    # TODO(18F): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    'psycopg2==2.7.3.1',
]

setup(
    name='sql_insert_writer',
    version='0.1.0',
    description="Helps make long SQL INSERT statements readable",
    long_description=readme + '\n\n' + history,
    author="18F",
    author_email='catherine.devlin@gsa.gov',
    url='https://github.com/18F/sql_insert_writer',
    packages=find_packages(include=['sql_insert_writer']),
    entry_points={
        'console_scripts': [
            'sql_insert_writer=sql_insert_writer.cli:main',
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="CC0 license",
    zip_safe=False,
    keywords='sql_insert_writer',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
