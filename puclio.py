#!/usr/bin/python3

#
# A Putio Utility, Command LIne Oriented.
#
# TODO:
#       - setup,
#       - manage bad token,
#       - use config parser.

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

    parser_ls = subparsers.add_parser('ls')
    parser_setup = subparsers.add_parser('setup')
    return p

def init_account():
    config = configparser.ConfigParser()

    try:
        config.read_file(open(os.path.expanduser(CONFIG_PATH)))
    except FileNotFoundError:
        print("No configuration file.")
        setup_account(config)

    token = config['account']['token']

    return putio2.Client(token)


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
        files = putio.File.list()
        for idx, f in enumerate(files):
            print(str(idx + 1) + "    " + f.name)

