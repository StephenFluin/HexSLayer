#!/usr/bin/python

import sys
sys.path.insert(0, 'buildlib/jinja2.egg')
sys.path.insert(0, 'buildlib')

# import zlib
# zlib.Z_DEFAULT_COMPRESSION = 9

import tarfile
import os
import shutil
import subprocess
import time
import StringIO

import jinja2

# The extension of the android and ant commands.
if os.name == "nt":
    ANDROID = "android.bat"
    ANT = "ant.bat"
else:
    ANDROID = "android"
    ANT = "ant"

# Try to find a host version of Python that matches our ARM version.
PYTHON = None
for b in ['python','python2.7','python2']:
    try:
        if subprocess.check_output(
                [b,'--version'],
                stderr=subprocess.STDOUT
                ).startswith('Python 2.7.1'):
            PYTHON = b
            break
    except OSError:
        pass

# Files and extensions we should not package.
BLACKLIST_FILES = [
    "icon.ico",
    "icon.icns",
    "launcherinfo.py",
    ".nomedia",
    ]

BLACKLIST_EXTENSIONS = [
    "~",
    ".bak",
    ".rpy",
    ".swp",
    ]

BLACKLIST_DIRS = [
    ".hg",
    ".git",
    ".bzr",
    ".svn",
    ]

# Used by render.
environment = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

def render(template, dest, **kwargs):
    """
    Using jinja2, render `template` to the filename `dest`, supplying the keyword
    arguments as template parameters.
    """

    template = environment.get_template(template)
    text = template.render(**kwargs)

    f = file(dest, "wb")
    f.write(text.encode("utf-8"))
    f.close()
    
def compile_dir(dfn):
    """
    Compile *.py in directory `dfn` to *.pyo
    """

    # -OO = strip docstrings
    subprocess.call([PYTHON,'-OO','-m','compileall','-f',dfn])

def make_tar(fn, source_dirs):
    """
    Make a zip file `fn` from the contents of source_dis.
    """

    # zf = zipfile.ZipFile(fn, "w")
    tf = tarfile.open(fn, "w:gz")

    
    for sd in source_dirs:
        if ".py" in BLACKLIST_EXTENSIONS:
            compile_dir(sd)
    
        sd = os.path.abspath(sd)    
    
        for dir, dirs, files in os.walk(sd):
            for bd in BLACKLIST_DIRS:
                if bd in dirs:
                    dirs.remove(bd)

            for fn in dirs:
                fn = os.path.join(dir, fn)
                relfn = os.path.relpath(fn, sd)
                tf.add(fn, relfn, recursive=False)

            for fn in files:        
                fn = os.path.join(dir, fn)
                relfn = os.path.relpath(fn, sd)

                bl = False
                for e in BLACKLIST_EXTENSIONS:
                    if relfn.endswith(e):
                        bl = True

                if bl:
                    continue

                if relfn in BLACKLIST_FILES:
                    continue

                tf.add(fn, relfn)

    # TODO: Fix me.
    # tf.writestr(".nomedia", "")
    tf.close()

    
def make_package(args):
    version_code = 0

    manifest_extra = '<uses-feature android:glEsVersion="0x00020000" />'
    url_scheme = "pygame"
    default_icon = "templates/pygame-icon.png"
    default_presplash = "templates/pygame-presplash.png"

        
    # Figure out the version code, if necessary.
    if not args.numeric_version:
        for i in args.version.split("."):
            version_code *= 100
            version_code += int(i)

        args.numeric_version = str(version_code)

    versioned_name = args.name.replace(" ", "").replace("'", "") + "-" + args.version

    if not args.icon_name:
        args.icon_name = args.name

    # Annoying fixups.
    args.name = args.name.replace("'", "\\'")
    args.icon_name = args.icon_name.replace("'", "\\'")
    
    # Figure out versions of the private and public data.
    private_version = str(time.time())

    if args.dir:
        public_version = private_version
    else:
        public_version = None
            
    # Render the various templates into control files.
    render(
        "AndroidManifest.tmpl.xml",
        "AndroidManifest.xml", 
        args = args,
        url_scheme = url_scheme,
        manifest_extra = manifest_extra,
        )

    render(
        "build.xml",
        "build.xml",
        args = args,
        versioned_name = versioned_name)

    render(
        "strings.xml",
        "res/values/strings.xml",
        public_version = public_version,
        private_version = private_version,
        url_scheme = url_scheme,
        args=args)

    # Update the project to a recent version.
    subprocess.call([ANDROID, "update", "project", "-p", '.', '-t', 'android-8'])

    # Delete the old assets.
    if os.path.exists("assets/public.mp3"):
        os.unlink("assets/public.mp3")

    if os.path.exists("assets/private.mp3"):
        os.unlink("assets/private.mp3")
        
    
    # Package up the private and public data.
    if args.private:
        make_tar("assets/private.mp3", [ 'private', args.private ])
    else:
        make_tar("assets/private.mp3", [ 'private' ])

    if args.dir:
        make_tar("assets/public.mp3", [ args.dir ])

    # Copy over the icon and presplash files.
    shutil.copy(args.icon or default_icon, "res/drawable/icon.png")
    shutil.copy(args.presplash or default_presplash, "res/drawable/presplash.png")

    # Build.
    subprocess.call([ANT, args.command])

def shelve_lib(lfn):
    for root,dirs,files in os.walk('libs'):
        for fn in files:
            if fn == lfn:
                shelf_dir = os.path.join('.shelf', root)
                if not os.path.exists(shelf_dir):
                    os.makedirs(shelf_dir)
                shutil.move(os.path.join(root,fn), shelf_dir)

def unshelve_libs():
    if os.path.exists('.shelf'):
        for root,dirs,files in os.walk('.shelf'):
            for fn in files:
                lib_dir = root[len('.shelf/'):]
                shutil.move(os.path.join(root,fn), lib_dir)
        shutil.rmtree('.shelf')


if __name__ == "__main__":
    import argparse
    
    ap = argparse.ArgumentParser(description="""\
Package a Pygame for Android or Ren'Py for Android project.

For this to work, Java and Ant need to be in your path, as does the
tools directory of the Android SDK.
""")

    ap.add_argument("--package", dest="package", help="The name of the java package the project will be packaged under.", required=True)
    ap.add_argument("--name", dest="name", help="The human-readable name of the project.", required=True)
    ap.add_argument("--version", dest="version", help="The version number of the project. This should consist of numbers and dots, and should have the same number of groups of numbers as previous versions.", required=True)
    ap.add_argument("--numeric-version", dest="numeric_version", help="The numeric version number of the project. If not given, this is automatically computed from the version.")
    ap.add_argument("--dir", dest="dir", help="The directory containing public files for the project.")
    ap.add_argument("--private", dest="private", help="The directory containing additional private files for the project.")
    ap.add_argument("--launcher", dest="launcher", action="store_true", help="Provide this argument to build a multi-game lanucher, rather than a single game.")
    ap.add_argument("--icon-name", dest="icon_name", help="The name of the project's launcher icon.")
    ap.add_argument("--orientation", dest="orientation", default="landscape", help="The orientation that the game will display in. Usually one of 'landscape' or 'portrait'.")
    ap.add_argument("--permission", dest="permissions", action='append', help="The permissions to give this app.")
    ap.add_argument("--icon", dest="icon", help="A png file to use as the icon for the application.")
    ap.add_argument("--presplash", dest="presplash", help="A jpeg file to use as a screen while the application is loading.")
    ap.add_argument("--install-location", dest="install_location", default="auto", help="The default install location. Should be 'auto', 'preferExternal' or 'internalOnly'.")
    ap.add_argument("--compile-pyo", dest="compile_pyo", action="store_true", help="Compile all .py files to .pyo, and only distribute the compiled bytecode.")
    ap.add_argument("--with-sqlite3", dest="with_sqlite3", action="store_true", help="Include sqlite3 module.")
    ap.add_argument("--with-PIL", dest="with_PIL", action="store_true", help="Include the Python Imaging Library (PIL).")
        
    ap.add_argument("command",  help="The command to pass to ant.")
    
    args = ap.parse_args()

    if not args.dir and not args.private and not args.launcher:
        ap.error("One of --dir, --private, or --launcher must be supplied.")

    if args.permissions is None:
        args.permissions = [ ]

    if args.compile_pyo:
        if PYTHON is None:
            ap.error("To use --compile-pyo, you need Python 2.7.1 installed and in your PATH.")
        BLACKLIST_EXTENSIONS += [".py", ".pyc"]

    if not args.with_sqlite3:
        BLACKLIST_DIRS += ['sqlite3']
        BLACKLIST_FILES += ['_sqlite3.so']
        shelve_lib('libsqlite3.so')

    if not args.with_PIL:
        BLACKLIST_DIRS += ['PIL']
        BLACKLIST_FILES += ['_imaging.so','_imagingft.so','_imagingmath.so']
        
    make_package(args)
    unshelve_libs()


