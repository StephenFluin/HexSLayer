mkdir -p debian/usr/share/pixmaps
mkdir -p debian/usr/share/games/hexslayer

cp ../gameicon.png debian/usr/share/pixmaps/hexslayer.png
cp ../*.png debian/usr/share/games/hexslayer/
py_compilefiles ../*.py
mv ../*.pyc debian/usr/share/games/hexslayer




dpkg -b debian hexslayer-`date +%Y%m%d`.deb

#Clean Up
rm debian/usr/share/pixmaps/hexslayer.png
rm debian/usr/share/games/hexslayer/*.png
rm debian/usr/share/games/hexslayer/*.pyc
