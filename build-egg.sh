#!/bin/bash

echo Building documentation...
cd doc
make html
cd ..

echo Building egg...
python -O setup.py sdist bdist_egg
# bdist_wininst no funciona por un error de encoding (mbcs)
