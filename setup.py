#!/usr/bin/env python
# -*- coding: latin-1 -*-

#-------------------------------------------------------------------------------
# Copyright (C) 2011 Francisco Dibar

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#-------------------------------------------------------------------------------

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
