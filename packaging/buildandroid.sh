#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64/
VERSION=`cat ../version.txt`
cd ../
python -c "import main"
cd packaging/android
mkdir tmp
cp ../../*.py tmp/
cp ../../*.png tmp/
#cp ../../main.py tmp/
cp ../../*.ttf tmp/
cp ../../version.txt tmp/

cd pygame-package-0.9.3

rm bin/HexSLayer*
rm bin/classes.*
if [ "${2}" != "headless" ]
then
	adb uninstall com.mortalpowers.android.hexslayer
fi
TYPE="release"
if [ "${1}" != "release" ]
then
    TYPE="debug"
fi
./build.py --package "com.mortalpowers.android.hexslayer" --name "HexSLayer" --version "$VERSION" --numeric-version 13 --private ../tmp --permission INTERNET --icon /super/workspace/HexSLayer/gameicon.png ${TYPE}
rm -r ../tmp

if [ "${TYPE}" = "release" ]
then
	
	cd bin
	/usr/lib/jvm/java-6-openjdk/bin/jarsigner -verbose -keystore /super/documents/mine/keys/hexslayer-androidmarket.keystore HexSLayer-$VERSION-release-unsigned.apk hexslayer
	/opt/android-sdk/tools/zipalign -v 4 HexSLayer-$VERSION-release-unsigned.apk HexSLayer-$VERSION-release.apk
	if [ "${2}" != "headless" ]
	then
		adb install -r HexSLayer-$VERSION-release.apk
	fi
else
	
	if [ "${2}" != "headless" ]
	then
		adb install -r bin/HexSLayer-$VERSION-debug.apk
	fi
fi

if [ "${2}" != "headless" ]
then
	adb shell am start -a android.intent.action.MAIN -n com.mortalpowers.android.hexslayer/org.renpy.android.PythonActivity
fi
