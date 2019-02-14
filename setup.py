#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ["pandas",
                "numpy",
                "flopy",
                "pyshp"]

setup_requirements = []

test_requirements = []

setup(
    author="Ayman Alzraiee, Joshua Larsen",
    author_email='aalzraiee@usgs.gov, jlarsen@usgs.gov',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='gsflow',
    name='gsflow',
    packages=find_packages(include=['gsflow',
                                    'gsflow.prms',
                                    'gsflow.utils',
                                    'gsflow.modflow',
                                    'gsflow.output']),
    setup_requires=setup_requirements,
    test_suite='autotest',
    tests_require=test_requirements,
    url='https://github.com/aymanalz/gsflow',
    version='0.1.0',
    zip_safe=False,
)
