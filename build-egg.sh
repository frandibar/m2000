#!/usr/bin/env bash

# build documentation
cd doc
make html
cd ..

python -O setup.py sdist bdist_egg 
# bdist_wininst no funciona por un error de encoding (mbcs)
