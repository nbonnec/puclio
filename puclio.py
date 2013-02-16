#!/usr/bin/python3

#
# A Putio Utility, Command LIne Oriented.
#

import argparse
import ressources.lib.putio2.putio2 as putio2
import sys

o_token = "STAZXOCH"

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description =
            "A Putio Utility, Command LIne Oriented.")
    subparsers = parser.add_subparsers(dest='cmd')

    parser_ls = subparsers.add_parser('ls')

    if len(sys.argv) == 1:
        parser.print_help();
        sys.exit(1)
    args = parser.parse_args()

    if args.cmd == 'ls':
        putio = putio2.Client(o_token)
        files = putio.File.list()
        for idx, f in enumerate(files):
            print(str(idx + 1) + "    " + f.name)

