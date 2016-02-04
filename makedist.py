#!/usr/bin/env python3

# Usage: python3 makedist.py
#
# This script copies the working files (everything needed to run Lectrote)
# into prebuilt Electron app packages. Fetch these from
#    https://github.com/atom/electron/releases
# and unzip them into a "dist" directory.

import sys
import os, os.path
import optparse
import shutil
import subprocess

lectrote_version = '0.1.2'

all_packages = [
    'darwin-x64',
    'linux-ia32',
    'linux-x64',
    'win32-ia32',
    'win32-x64',
]

popt = optparse.OptionParser()

popt.add_option('-b', '--build',
                action='store_true', dest='makedist',
                help='build dist directories')
popt.add_option('-z', '--zip',
                action='store_true', dest='makezip',
                help='turn dist directories into zip files')

(opts, args) = popt.parse_args()


files = [
    './package.json',
    './main.js',
    './apphooks.js',
    './play.html',
    './about.html',
    './if-card.html',
    './el-glkote.css',
    './icon-128.png',
    './quixe/lib/elkote.min.js',
    './quixe/lib/jquery-1.11.2.min.js',
    './quixe/lib/quixe.min.js',
    './quixe/media/waiting.gif',
]

def install(resourcedir):
    if not os.path.isdir(resourcedir):
        raise Exception('path does not exist: ' + resourcedir)
    appdir = resourcedir
    print('Installing to: ' + appdir)
    
    os.makedirs(appdir, exist_ok=True)
    qdir = os.path.join(appdir, 'quixe')
    os.makedirs(qdir, exist_ok=True)
    os.makedirs(os.path.join(qdir, 'lib'), exist_ok=True)
    os.makedirs(os.path.join(qdir, 'media'), exist_ok=True)
    
    for filename in files:
        shutil.copyfile(filename, os.path.join(appdir, filename))

def builddir(dir, pack):
    cmd = 'npm run package-%s' % (pack,)
    subprocess.call(cmd, shell=True)

    shutil.copyfile('LICENSE', os.path.join(dir, 'LICENSE'))
    os.unlink(os.path.join(dir, 'version'))
    
def makezip(dir, unwrapped=False):
    prefix = 'Lectrote-'
    val = os.path.split(dir)[-1]
    if not val.startswith(prefix):
        raise Exception('path does not have the prefix')
    zipfile = 'Lectrote-' + lectrote_version + '-' + val[len(prefix):]
    print('Zipping up: %s to %s (%s)' % (dir, zipfile, ('unwrapped' if unwrapped else 'wrapped')))
    if unwrapped:
        subprocess.call('cd %s; rm -f ../%s.zip; zip -q -r ../%s.zip *' % (dir, zipfile, zipfile),
                        shell=True)
    else:
        dirls = os.path.split(dir)
        subdir = dirls[-1]
        topdir = os.path.join(*os.path.split(dir)[0:-1])
        subprocess.call('cd %s; rm -f %s.zip; zip -q -r %s.zip %s' % (topdir, zipfile, zipfile, subdir),
                        shell=True)

print('Lectrote version: %s' % (lectrote_version,))

packages = []
if not args:
    packages = all_packages
else:
    for pack in all_packages:
        for arg in args:
            if arg in pack:
                packages.append(pack)
                break

if not packages:
    raise Exception('no packages selected')

install('tempapp')

if opts.makedist:
    for pack in packages:
        dest = 'dist/Lectrote-%s' % (pack,)
        builddir(dest, pack)

if opts.makezip:
    for pack in packages:
        dest = 'dist/Lectrote-%s' % (pack,)
        makezip(dest, unwrapped=('win32' in pack))
