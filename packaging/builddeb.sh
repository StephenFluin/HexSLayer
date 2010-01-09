mkdir -p usr/share/pixmaps
cp ../gameicon.png usr/share/pixmaps/hexslayer.png

dpkg -b filesystem hexslayer-`date +%Y%m%d`.deb`
