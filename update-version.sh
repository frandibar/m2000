#!/bin/bash

if [ $# -ne 1 ]
    then echo "usage: ./update-version.sh [version]"
    exit
fi

echo Updating update-win.bat
sed -e s/__VERSION__/"$1"/g update-win-template.bat > update-win.bat

echo Updating m2000/__init__.py
sed -i 23d m2000/__init__.py
echo "__version__ = '""$1""'" >> m2000/__init__.py

