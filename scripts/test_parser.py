#!/usr/bin/env python

import sys

from tecan_reader import parse

if __name__ == '__main__' :

    print parse(sys.argv[1])
