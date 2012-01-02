#!/bin/bash
cd ../
python -c "import main"
cd packaging/android
mkdir tmp
cp ../../*.py tmp/
cp ../../*.png tmp/
#cp ../../main.py tmp/
cp ../../freesansbold.ttf tmp/

cd pygame-package-0.9.3
rm bin/*
./build.py --package "com.mortalpowers.android.hexslayer" --name "HexSLayer" --version "1.0.6" --numeric-version 4 --private ../tmp --permission INTERNET --icon /super/workspace/HexSLayer/gameicon.png debug
rm build.xml
rm -r ../tmp
android update project -p ./ -n HexSLayer
ant debug
adb install -r bin/HexSLayer-debug-unaligned.apk