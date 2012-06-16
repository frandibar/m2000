#!/bin/bash

if [ $# -ne 1 ]; then
    echo "usage: `basename $0` [version]"
    echo "example: `basename $0` 12.6.16.6"
    exit 1
fi

version=$1

./update-version.sh $version
./build-egg.sh

# crear un archivo llamado v[version].zip que contenga
# + m2000-[version]-py2.7.egg
# + update-win.bat
# + firma-tesorero.png
# + firma-presidente.png
# + base.py (hasta la proxima version de camelot)
echo Making zip file...
zip v$version.zip -j dist/m2000-$version-py2.7.egg update-win.bat m2000/media/firma-tesorero.png m2000/media/firma-presidente.png base.py
mv v$version.zip ~/Dropbox/m2000

git ci update-win.bat m2000/__init__.py changelog.org -m"new release"
git tag -a v$version -m"new release"
git push --tags

./update-version.sh master
git ci update-win.bat m2000/__init__.py -m"post release"
