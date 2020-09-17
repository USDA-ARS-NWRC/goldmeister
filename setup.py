#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('docs/HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as req:
    requirements = req.read()


setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="USDA-ARS-NWRC",
    author_email='snow@ars.usda.gov',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python package for comparing dataset changes in a repos that have output files they check",
    install_requires=requirements,
    license="CC0 1.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='goldmeister',
    name='goldmeister',
    packages=find_packages(include=['goldmeister', 'goldmeister.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/USDA-ARS-NWRC/goldmeister',
    version='0.2.0',
    zip_safe=False,
)
