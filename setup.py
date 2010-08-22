#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup
import glob
import time
import string
import re
import sys
import glob

try:
    from lxml.etree import Element,ElementTree
except:
    print "Without lxml, this program will fail. Aborting."
    print "Get it at http://codespeak.net/lxml/"
    sys.exit(1)

try:
    import py2exe
except ImportError, e:
    pass

try:
    import py2app
except ImportError, e:
    pass

try:
    import wxversion
    wxversion.ensureMinimal("2.8")
    import wx
except:
    print "Without wx, this program will fail. Aborting."
    print "Get it at http://www.wxpython.org/"
    sys.exit(1)

import geocacher


# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None
import os

from distutils.command.install_data import install_data
class smart_install_data(install_data):
    def run(self):
        #need to change self.install_dir to the library dir
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        return install_data.run(self)

def find_data_files(source,target,patterns):
    """Locates the specified data-files and returns the matches
    in a data_files compatible format.

    source is the root of the source data tree.
        Use '' or '.' for current directory.
    target is the root of the target data tree.
        Use '' or '.' for the distribution directory.
    patterns is a sequence of glob-patterns for the
        files you want to copy.
    """
    if glob.has_magic(source) or glob.has_magic(target):
        raise ValueError("Magic not allowed in src, target")
    ret = {}
    for pattern in patterns:
        pattern = os.path.join(source,pattern)
        for filename in glob.glob(pattern):
            if os.path.isfile(filename):
                targetpath = os.path.join(target,os.path.relpath(filename,source))
                path = os.path.dirname(targetpath)
                ret.setdefault(path,[]).append(filename)
    return sorted(ret.items())

def is_package( filename ):
    return(
        os.path.isdir(filename) and
        os.path.isfile(os.path.join(filename,'__init__.py'))
    )

def find_packages( filename, basePackage="" ):
    """Find all packages in filename"""
    set = {}
    for item in os.listdir(filename):
        dir = os.path.join(filename, item)
        if is_package( dir ):
            if basePackage:
                moduleName = basePackage+'.'+item
            else:
                moduleName = item
            set[ moduleName] = dir
            set.update( find_packages( dir, moduleName))
    return set

srcPath = '.'
# generate the build number

packages = find_packages(srcPath)
dataFiles = find_data_files('geocacher','geocacher',[
    'xrc/*.xrc',
    'gfx/*.png',
    'gfx/*.gif',
    'gfx/*.ico',
    'gfx/*.jpg',
    'gfx/*/*/*.png',
    'gfx/*/*/*.gif',
    'gfx/*/*/*.ico',
    'gfx/*/*/*.jpg'])

setup(
    name="geocacher",
    description=geocacher.appdescription,
    long_description=geocacher.appdescription,
    version=geocacher.version,
    license="GPL-2",
    author=geocacher.author,
    author_email=geocacher.authoremail,
    maintainer=geocacher.author,
    maintainer_email=geocacher.authoremail,
    url=geocacher.website,
    scripts=['gcer',],
    packages=packages,#['geocacher',],
    #package_data = dataFiles,
    cmdclass = {'install_data':smart_install_data},
    # Options for py2exe
    options = {"py2exe": {"dll_excludes": ["user32.dll", "ole32.dll",
                                           "kernel32.dll", "rpcrt4.dll",
                                           "oleaut32.dll", "shell32.dll",
                                           "shlwapi.dll", "ntdll.dll",
                                           "comdlg32.dll", "wsock32.dll",
                                           "comctl32.dll", "advapi32.dll",
                                           "ws2_32.dll", "gdi32.dll",
                                           "winmm.dll", "ws2help.dll",
                                           "mswsock.dll", "MSVCP90.dll"]
        }
    },
    windows=[{'script': 'gcer'}],
    data_files=dataFiles,

    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License Version 3 (GPL-V3)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
)

