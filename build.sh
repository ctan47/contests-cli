#!/usr/bin/env bash

if [ -e build ]; then rm -rf build; fi
if [ -e dist ]; then rm -rf dist; fi
if [ -e contests.spec ]; then rm contests.spec; fi
if [ -e contests.zip ]; then rm contests.zip; fi

if [ -e "venv" ]
then
    source venv/bin/activate
else
    echo "venv not found"
    exit
fi

python -m PyInstaller contests.py >/dev/null 2>&1

cd dist && zip -rq9 contests.zip contests

echo " move dist/contests.zip archive into"
echo " current directory using following command"
echo "     mv dist/contests.zip ."
