mkdir -p debian/usr/share/pixmaps
mkdir -p debian/usr/share/games/hexslayer

cp ../gameicon.png debian/usr/share/pixmaps/hexslayer.png

py_compilefiles ../*.py
mv ../*.pyc debian/usr/share/games/hexslayer




dpkg -b debian hexslayer-`date +%Y%m%d`.deb`
