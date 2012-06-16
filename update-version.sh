#!/bin/bash

if [ $# -ne 1 ]; then
    echo "usage: `basename $0` [version]"
    echo "example: `basename $0` 12.6.16.6"
    exit
fi

version=$1

echo Updating update-win.bat...
sed -i "s/^set version=.*/set version=$version/" update-win.bat

echo Updating m2000/__init__.py...
sed -i 23d m2000/__init__.py
echo __version__ = \'$version\' >> m2000/__init__.py
