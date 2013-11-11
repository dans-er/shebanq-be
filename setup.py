#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup

setup(
    name = "shebanq-be",
    version = "0.1.0",
    author = "Henk van den Berg",
    author_email = "henkvandenberg8@gmail.com",
    description = ("Bridge between Emdros and CLAM"),
    license = "Apache-2.0",
    keywords = "emdros clam webservice rest mql",
    url = "http://dans.knaw.nl",
    packages=['emdros'],
    # long_description=read('README'),
    install_requires=['clam']
)

