#!/usr/bin/python3

#
# A Putio Utility, Command LIne Oriented.
#
# TODO:
#       - manage bad token,

import argparse
import configparser
import logging
import os
import sys
from ressources.lib.putio2 import putio2

CONFIG_PATH = "~/.config/puclio/config"
PUTIO_APP_ID = "337"
PUTIO_TOKEN_PATH = "http://put.io/v2/oauth2/apptoken/" + PUTIO_APP_ID

def setup_account():
    config = configparser.ConfigParser()
    tok = input("To get your Oauth token go to: " + PUTIO_TOKEN_PATH +
                ".\nOauth token ? ")
    config.add_section('account')
    config.set('account', 'token', tok)
    with open(os.path.expanduser(CONFIG_PATH), 'w') as configfile:
        config.write(configfile)

def init_parser():
    p = argparse.ArgumentParser(description =
            "A Putio Utility, Command LIne Oriented.")
    subparsers = p.add_subparsers(dest='cmd')

    parser_ls = subparsers.add_parser('ls', help = "list files")
    parser_ls.add_argument("-a", "--all", help = "show more informations",
            action = "store_true")
    parser_ls.add_argument("id", type = int, nargs = '?', default = 0,
            help = "ID to list")
    parser_setup = subparsers.add_parser('setup',
            help = "setup your Oauth account")
    return p

def init_account():
    config = configparser.ConfigParser()

    try:
        config.read_file(open(os.path.expanduser(CONFIG_PATH)))
    except FileNotFoundError:
        print("No configuration file.")
        setup_account(config)

    try:
        token = config['account']['token']
    except KeyError:
        print("Problem with the configuration file. \n"
                "Try to run " + sys.argv[0] + " setup.")
        exit(1)

    return putio2.Client(token)

def list_files(putio, args = None):
        files = putio.File.list(args.id)
        for idx, f in enumerate(files):
            yield "{0:>3}    {1}".format(idx + 1, f.name)

if __name__ == "__main__":

    parser = init_parser()

    if len(sys.argv) == 1:
        parser.print_help();
        sys.exit(1)
    args = parser.parse_args()

    if args.cmd == 'setup':
        setup_account()
        exit(0)

    putio = init_account()

    if args.cmd == 'ls':
        for files in list_files(putio, args):
            print(files)

