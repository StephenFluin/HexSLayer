#!/bin/bash
cd ../
python -c "import main"
cd packaging/android
mkdir tmp
cp ../../*.py tmp/
cp ../../*.png tmp/
#cp ../../main.py tmp/
cp ../../*.ttf tmp/

cd pygame-package-0.9.3
rm bin/*
./build.py --package "com.mortalpowers.android.hexslayer" --name "HexSLayer" --version "1.0.8" --numeric-version 6 --private ../tmp --permission INTERNET --icon /super/workspace/HexSLayer/gameicon.png debug
rm build.xml
rm -r ../tmp
android update project -p ./ -n HexSLayer
if [ "${1}" = "release" ]
then
	ant release
	cd bin
	/usr/lib/jvm/java-6-openjdk/bin/jarsigner -verbose -keystore /super/documents/mine/keys/hexslayer-androidmarket.keystore HexSLayer-release-unsigned.apk hexslayer
	/opt/android-sdk/tools/zipalign -v 4 HexSLayer-release-unsigned.apk HexSLayer-release.apk
	adb install -r HexSLayer-release.apk
else
	ant debug
	adb install -r bin/HexSLayer-debug-unaligned.apk
fi

adb shell am start -a android.intent.action.MAIN -n com.mortalpowers.android.hexslayer/org.renpy.android.PythonActivity