#!/bin/bash
cd pygame-package-0.9.3
rm bin/*
./build.py --package "com.mortalpowers.android.hexslayer" --name "HexSLayer" --version "1.1" --numeric-version 2 --private /super/workspace/HexSLayer/ --permission INTERNET --icon /super/workspace/HexSLayer/gameicon.png debug
rm build.xml
android update project -p ./ -n HexSLayer
ant debug
adb install -r bin/HexSLayer-debug-unaligned.apk