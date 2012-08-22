#!/usr/bin/env python

import os
import sys

from distutils.core import setup

scripts = [ ]

# setup and install
setup(name='tecan_reader',
      version='0.1',
      author='Adam Labadorf',
      author_email='alabadorf@gmail.com',
      package_dir={'':'src'},
      py_modules=['tecan_reader.parser','tecan_reader.base'],
      packages=['tecan_reader'],
      scripts=scripts
     )
