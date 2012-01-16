#!/usr/bin/env python

import os, sys, subprocess
from optparse import *

#Based on Gouichi Iisaka graphviz filter"
__AUTHOR__ = "Bartosz Wiklak <bwiklak@gmail.com>"
__VERSION__ = '1.0.0'

class EApp(Exception):
    '''Application specific exception.'''
    pass

class Application():
    '''
NAME
    acplantuml - Converts textual Plantuml notation to PNG, SVG or EPS file

SYNOPSIS
    acplantuml [options] INFILE

DESCRIPTION
    This filter reads Plantuml notation text from the input file
    INFILE (or stdin if INFILE is -), converts it to a PNG, SVG or EPS image file.


OPTIONS
    -o OUTFILE, --outfile=OUTFILE
        The file name of the output file. If not specified the output file is
        named like INFILE but with a .png file name extension.

    -F FORMAT, --format=FORMAT
        Graphviz output format: png, svg, or any other format Graphviz
        supports. Run dot -T? to get the full list.
        Default is 'png'.

    -v, --verbose
        Verbosely print processing information to stderr.

    -h, --help
        Print this documentation.

    -V, --version
        Print program version number.

SEE ALSO
    graphviz(1)

AUTHOR
    Written by Bartosz Wiklak, <bwiklak@gmail.com>

THANKS
    Gouichi Iisaka <iisaka51@gmail.com>
    This script was inspired by his graphviz2png.py and AsciiDoc

LICENSE
    Copyright (C) 2012-2013 Bartosz Wiklak.
    Free use of this software is granted under the terms of
    the GNU General Public License (GPL).
    '''

    def __init__(self, argv=None):
        if not argv:
            argv = sys.argv

        self.usage = '%prog [options] inputfile'
        self.version = 'Version: %s\n' % __VERSION__
        self.version += 'Copyright(c) 2012-2013: %s\n' % __AUTHOR__

        self.option_list = [
            Option("-o", "--outfile", action="store",
                dest="outfile",
                help="Output file"),
            Option("-F", "--format", action="store",
                dest="format", default="png", type="choice",
                choices=['png','svg','eps'],
                help="Supported formats (svg, eps, png)"),
            Option("--debug", action="store_true",
                dest="do_debug",
                help=SUPPRESS_HELP),
            Option("-v", "--verbose", action="store_true",
                dest="do_verbose", default=False,
                help="verbose output"),
            ]

        self.parser = OptionParser( usage=self.usage, version=self.version,
                                    option_list=self.option_list)
        (self.options, self.args) = self.parser.parse_args()

        if len(self.args) != 1:
            self.parser.print_help()
            sys.exit(1)

        self.options.infile = self.args[0]

    def systemcmd(self, cmd):
        if self.options.do_verbose:
            msg = 'Execute: %s' % cmd
            sys.stderr.write(msg + os.linesep)
        else:
            cmd += ' 2>%s' % os.devnull
        if os.system(cmd):
            raise EApp, 'failed command: %s' % cmd

    def acplantuml(self, infile, outfile):
        '''Convert Plantuml notation in file infile to
           named outfile.'''

        outfile = os.path.abspath(outfile)
        outdir = os.path.dirname(outfile)

        if not os.path.isdir(outdir):
            raise EApp, 'directory does not exist: %s' % outdir

        basefile = os.path.splitext(outfile)[0]
        saved_cwd = os.getcwd()
        filter_path = os.path.dirname(__file__)
        os.chdir(outdir)

        try:
            cmd = 'java -jar %s/plantuml.jar -T%s -quiet "%s" > "%s"' % (
                  filter_path, self.options.format, infile, outfile)
            self.systemcmd(cmd)
        finally:
            os.chdir(saved_cwd)

        if not self.options.do_debug:
            os.unlink(infile)

    def run(self):
        if self.options.format == '':
            self.options.format = 'png'

        if self.options.outfile is None:
            outfile = os.path.splitext(infile)[0] + '.png'
        else:
            outfile = self.options.outfile

        if self.options.infile == '-':
            if self.options.outfile is None:
                sys.stderr.write('OUTFILE must be specified')
                sys.exit(1)
            infile = os.path.splitext(self.options.outfile)[0] + '.txt'
            lines = sys.stdin.readlines()
            lines = filter( lambda s: not 'startuml' in s, lines )
            lines = filter( lambda s: not 'enduml' in s, lines )
            lines.insert(0,'@startuml\n')
            lines.append('\n')
            lines.append('@enduml')
            open(infile, 'w').writelines(lines)

        if not os.path.isfile(infile):
            raise EApp, 'input file does not exist: %s' % infile

        self.acplantuml(infile, outfile)

        # To suppress asciidoc 'no output from filter' warnings.
        if self.options.infile == '-':
            sys.stdout.write(' ')

if __name__ == "__main__":
    app = Application()
    app.run()
