#!/usr/bin/env bash

python -O setup.py sdist bdist_egg 
# bdist_wininst no funciona por un error de encoding (mbcs)
