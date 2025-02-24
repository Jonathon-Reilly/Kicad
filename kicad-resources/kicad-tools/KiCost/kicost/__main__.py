# MIT license
#
# Copyright (C) 2015 by XESS Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Inserted by Pasteurize tool.
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()

import argparse as ap
import os
import sys
import logging
import time
from .kicost import *
from . import __version__

NUM_PROCESSES = 30  # Maximum number of parallel web-scraping processes.

###############################################################################
# Command-line interface.
###############################################################################

def main():

    parser = ap.ArgumentParser(
        description='Build cost spreadsheet for a KiCAD project.')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='KiCost ' + __version__)
    parser.add_argument('-i', '--input',
                        nargs='?',
                        type=str,
                        metavar='file.xml',
                        help='Schematic BOM XML file.')
    parser.add_argument('-o', '--output',
                        nargs='?',
                        type=str,
                        metavar='file.xlsx',
                        help='Generated cost spreadsheet.')
    parser.add_argument('-var', '--variant',
                        nargs='?',
                        type=str,
                        default='',
                        help='schematic variant name filter')
    parser.add_argument('-w', '--overwrite',
                        action='store_true',
                        help='Allow overwriting of an existing spreadsheet.')
    parser.add_argument('-s', '--serial',
                        action='store_true',
                        help='Do web scraping of part data using a single process.')
    parser.add_argument('-np', '--num_processes',
                        nargs='?',
                        type=int,
                        default=NUM_PROCESSES,
                        const=NUM_PROCESSES,
                        metavar='NUM_PROCESSES',
                        help='''Set the number of parallel 
                            processes used for web scraping part data.''')
    parser.add_argument('-ign', '--ignore_fields',
                        nargs='+',
                        default=[],
                        help='Declare part fields to ignore when grouping parts.',
                        metavar='name',
                        type=str)
    parser.add_argument(
        '-d', '--debug',
        nargs='?',
        type=int,
        default=None,
        metavar='LEVEL',
        help='Print debugging info. (Larger LEVEL means more info.)')

    args = parser.parse_args()

    logger = logging.getLogger('kicost')
    if args.debug is not None:
        log_level = logging.DEBUG + 1 - args.debug
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        logger.addHandler(handler)
        logger.setLevel(log_level)

    if args.output == None:
        if args.input != None:
            args.output = os.path.splitext(args.input)[0] + '.xlsx'
        else:
            args.output = os.path.splitext(sys.argv[0])[0] + '.xlsx'
    else:
        args.output = os.path.splitext(args.output)[0] + '.xlsx'
    if os.path.isfile(args.output):
        if not args.overwrite:
            logger.critical('''Output file {} already exists! Use the
                --overwrite option to replace it.'''.format(args.output))
            sys.exit(1)

    if args.input == None:
        args.input = sys.stdin
    else:
        args.input = os.path.splitext(args.input)[0] + '.xml'
        args.input = open(args.input)

    if args.serial:
        num_processes = 1
    else:
        num_processes = args.num_processes

    kicost(in_file=args.input, out_filename=args.output, 
        ignore_fields=args.ignore_fields, variant=args.variant,
        num_processes=num_processes)

###############################################################################
# Main entrypoint.
###############################################################################
if __name__ == '__main__':
    start_time = time.time()
    main()
    logger = logging.getLogger('kicost')
    logger.log(logging.DEBUG-2, 'Elapsed time: %f seconds', time.time() - start_time)
