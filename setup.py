#!/usr/bin/env python

from distutils.core import setup, Extension
from distutils.cmd import Command
from distutils.command.build_ext import build_ext as _build_ext

import sys, os, subprocess

try:
    normaliz_dir = os.environ["NORMALIZ_LOCAL_DIR"]
except KeyError:
    extra_kwds = {}
else:
    extra_kwds = {
      "include_dirs": [ normaliz_dir + '/include'],
      "library_dirs": [ normaliz_dir + '/lib'],
      "runtime_library_dirs": [ normaliz_dir + '/lib'],
      "extra_link_args": ['-Wl,-R' + normaliz_dir + '/lib' ]
    }

libraries = [ 'normaliz', 'gmp', 'flint' ]

class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        old_path = os.getcwd()
        setup_path = os.path.dirname(__file__)
        tests_path = os.path.join(setup_path, 'tests')
        try:
            os.chdir(tests_path)

            if subprocess.call([sys.executable, 'runtests.py']):
                raise SystemExit("Doctest failures")

        finally:
            os.chdir(old_path)

class build_ext(_build_ext):
    def run(self):
        """
        Run ./configure first and update libraries depending
        on the generated output.
        """
        subprocess.check_call(["make", "configure"])
        try:
            subprocess.check_call(["sh", "configure"])
        except subprocess.CalledProcessError:
            subprocess.check_call(["cat", "config.log"])
            raise

        # configure created config.py that we now import
        from config import ENFNORMALIZ
        global libraries
        if ENFNORMALIZ:
            print("building with ENFNORMALIZ...")
            libraries.append("arb")
            libraries.append("eanticxx")
        else:
            print("no ENFNORMALIZ support...")

        _build_ext.run(self)

setup(
    name = 'PyNormaliz',
    version = '2.2',
    description = 'An interface to Normaliz',
    author = 'Sebastian Gutsche, Richard Sieg',
    author_email = 'sebastian.gutsche@gmail.com',
    url = 'https://github.com/Normaliz/PyNormaliz',
    py_modules = [ "PyNormaliz" ],
    ext_modules = [ Extension( "PyNormaliz_cpp",
                              [ "NormalizModule.cpp" ],
                              extra_compile_args=['-std=c++11'],
                              libraries=libraries,
                              **extra_kwds) ],
    
    package_data = {'': [ "COPYING", "GPLv2", "Readme.md" ] },
    cmdclass = {'build_ext': build_ext, 'test': TestCommand},
)
