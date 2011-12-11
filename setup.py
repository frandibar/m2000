#!/usr/bin/env python
# -*- coding: latin-1 -*-

from setuptools import setup, find_packages

setup(
    name = 'm2000',
    version = '0.1',
    description = u'Gestión de Créditos',
    author = 'Francisco Dibar',
    author_email = 'frandibar+m2000@gmail.com',
    maintainer = 'Francisco Dibar',
    maintainer_email = 'frandibar+m2000@gmail.com',
    url = 'www.mujeres2000.org.ar',
    install_requires = ['Camelot>=11.11.16'],
    include_package_data = True,
    packages = find_packages(),
    py_modules = ['settings', 'main'],
    entry_points = {'gui_scripts':[
            'main = main:start_application',
            ],},
    package_data = {
        # If any package contains these files, include them:
        '': ['*.txt', 
             '*.png',
             '*.html',
             '*.css',
             ],
        }
    )
