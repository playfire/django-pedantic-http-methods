#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-pedantic-http-methods',
    description="Raises an exception when attempting to perform side effects "
        "in GET and HEAD HTTP methods.",
    version='0.1',
    url='http://code.playfire.com/django-pedantic-http-methods',

    author='Playfire.com',
    author_email='tech@playfire.com',
    license='BSD',

    packages=find_packages(),
)
