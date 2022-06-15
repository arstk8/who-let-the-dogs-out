#!/bin/bash
cd "$(dirname "$0")" || exit
CWD=$(pwd)

ROOT_DIR="$CWD/.."
VIRTUALENV_NAME=env_who-let-the-dogs-out
PYTHON_RUNTIME=python3.8
DIST_DIRECTORY=dist

virtualenv -p $PYTHON_RUNTIME $VIRTUALENV_NAME
source "$VIRTUALENV_NAME/bin/activate"
pip install -r "$ROOT_DIR/requirements.txt"
deactivate

rm -rf $DIST_DIRECTORY
mkdir $DIST_DIRECTORY
cp -r "$CWD/$VIRTUALENV_NAME/lib/$PYTHON_RUNTIME/site-packages/" "$CWD/$DIST_DIRECTORY"
cp -r "$ROOT_DIR/src" "$CWD/$DIST_DIRECTORY"

rm -f dist.zip
cd $DIST_DIRECTORY || exit
zip -r9 -qq dist.zip *
mv dist.zip "$CWD"
cd ..
rm -rf $DIST_DIRECTORY