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
./build.py --package "com.mortalpowers.android.hexslayer" --name "HexSLayer" --version "1.0.7" --numeric-version 5 --private ../tmp --permission INTERNET --icon /super/workspace/HexSLayer/gameicon.png debug
rm build.xml
rm -r ../tmp
android update project -p ./ -n HexSLayer
ant debug
#ant release
#/usr/lib/jvm/java-6-openjdk/bin/jarsigner -verbose -keystore /super/documents/mine/keys/hexslayer-androidmarket.keystore HexSLayer-release-unsigned.apk hexslayer
#/opt/android-sdk/tools/zipalign -v 4 HexSLayer-release-unsigned.apk HexSlayer-release.apk
adb install -r bin/HexSLayer-debug-unaligned.apk
